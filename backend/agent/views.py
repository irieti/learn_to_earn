from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .models import User, Task, UserTask, LearningPath
from .ai_core import LearnEarnAIAgent
from .blockchain import issue_token_reward, mint_nft_badge
from time import timezone
from django.views.generic import TemplateView
from django.conf import settings
from telegram import Bot

logger = logging.getLogger(__name__)
ai_agent = LearnEarnAIAgent()


class FrontendView(TemplateView):
    template_name = "index.html"


def send_telegram_notification(user_telegram_id, task):
    try:
        # Skip if in testing or no token
        if not settings.TELEGRAM_BOT_TOKEN or getattr(settings, "TESTING", False):
            return False

        # Validate required fields
        if not all([user_telegram_id, task.id, task.title]):
            logger.warning("Invalid notification parameters")
            return False

        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        # Format message with emojis and Markdown
        message = (
            f"🎯 *New Task Available!*\n\n"
            f"**{task.title}**\n"
            f"📍 {task.description[:100]}...\n\n"
            f"🏆 Reward: {task.xp_reward} XP"
            f"{f' + {task.token_reward} LEARN' if task.token_reward else ''}\n"
            f"🔗 [Open in App]({settings.WEBAPP_URL}/task/{task.id})"
        )

        bot.send_message(
            chat_id=user_telegram_id,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        return True

    except Exception as e:
        logger.error(
            f"Telegram notification failed: {str(e)}",
            extra={"user_id": user_telegram_id, "task_id": task.id},
        )
        return False


# Helper functions
def get_request_data(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def error_response(message, status=400):
    return JsonResponse({"success": False, "error": message}, status=status)


def success_response(data=None):
    response = {"success": True}
    if data:
        response.update(data)
    return JsonResponse(response)


# System endpoints
@require_http_methods(["GET"])
def health_check(request):
    return success_response({"status": "healthy"})


# User onboarding flow
@csrf_exempt
@require_http_methods(["POST"])
def onboard_user(request):
    """Complete user onboarding and create initial learning path"""
    data = get_request_data(request)
    if not data or "telegram_id" not in data or "interest" not in data:
        return error_response("Telegram ID and interest are required")

    try:
        # Create or update user
        user, created = User.objects.get_or_create(
            telegram_id=data["telegram_id"],
            defaults={
                "interests": {"primary": data["interest"]},
                "wallet_address": data.get("wallet_address"),
            },
        )

        # Create initial learning path
        path_result = ai_agent.create_personalized_path(
            user.telegram_id, data["interest"]
        )
        if not path_result["success"]:
            return error_response(path_result["error"])

        # Get first task to start with
        first_task = (
            UserTask.objects.filter(user=user, learning_path_id=path_result["path_id"])
            .order_by("id")
            .first()
        )

        return success_response(
            {
                "onboarded": True,
                "path_id": path_result["path_id"],
                "first_task_id": first_task.id if first_task else None,
                "user_level": user.level,
            }
        )

    except Exception as e:
        logger.error(f"Onboarding error: {e}")
        return error_response(str(e))


# Learning path management
@csrf_exempt
@require_http_methods(["POST"])
def start_learning_path(request):
    """Start a new learning path for user"""
    data = get_request_data(request)
    if not data or "telegram_id" not in data or "topic" not in data:
        return error_response("Telegram ID and topic are required")

    try:
        result = ai_agent.create_personalized_path(data["telegram_id"], data["topic"])
        if result["success"]:
            return success_response(
                {"path_id": result["path_id"], "steps_count": result["steps_count"]}
            )
        return error_response(result["error"])
    except Exception as e:
        logger.error(f"Error creating learning path: {e}")
        return error_response(str(e))


@require_http_methods(["GET"])
def get_user_paths(request, telegram_id):
    """Get all learning paths for user"""
    try:
        user = User.objects.get(telegram_id=telegram_id)
        paths = LearningPath.objects.filter(user=user).order_by("-created_at")

        return success_response(
            {
                "paths": [
                    {
                        "id": path.id,
                        "topic": path.topic,
                        "status": path.status,
                        "created_at": path.created_at,
                        "progress": UserTask.objects.filter(
                            learning_path=path, status__in=["completed", "verified"]
                        ).count()
                        / UserTask.objects.filter(learning_path=path).count(),
                    }
                    for path in paths
                ]
            }
        )
    except User.DoesNotExist:
        return error_response("User not found", 404)
    except Exception as e:
        logger.error(f"Error getting user paths: {e}")
        return error_response(str(e))


# Task management
@require_http_methods(["GET"])
def get_current_task(request, telegram_id):
    """Get user's current active task"""
    try:
        user = User.objects.get(telegram_id=telegram_id)
        task = (
            UserTask.objects.filter(user=user, status__in=["active", "pending"])
            .order_by("id")
            .first()
        )

        if not task:
            return success_response({"has_task": False})

        # Generate content if it's a learning task
        content = {}
        if task.task.task_type == "learning":
            content_result = ai_agent.generate_lesson_content(task.task.id)
            if content_result["success"]:
                content = {
                    "lesson": content_result["lesson"],
                    "quiz": content_result["quiz"],
                }

        return success_response(
            {
                "has_task": True,
                "task_id": task.id,
                "title": task.task.title,
                "description": task.task.description,
                "type": task.task.task_type,
                "xp_reward": task.task.xp_reward,
                "token_reward": task.task.token_reward,
                "content": content,
            }
        )
    except User.DoesNotExist:
        return error_response("User not found", 404)
    except Exception as e:
        logger.error(f"Error getting current task: {e}")
        return error_response(str(e))


@csrf_exempt
@require_http_methods(["POST"])
def start_task(request, user_task_id):
    """Mark a task as started"""
    try:
        user_task = UserTask.objects.get(id=user_task_id)
        if user_task.status != "pending":
            return error_response("Task already started or completed")

        user_task.status = "active"
        user_task.started_at = timezone.now()
        user_task.save()

        return success_response({"task_id": user_task.id, "status": user_task.status})
    except UserTask.DoesNotExist:
        return error_response("Task not found", 404)
    except Exception as e:
        logger.error(f"Error starting task: {e}")
        return error_response(str(e))


@csrf_exempt
@require_http_methods(["POST"])
def verify_task(request, user_task_id):
    """Verify task completion with proof data"""
    data = get_request_data(request)
    if not data or "proof" not in data:
        return error_response("Proof data is required")

    try:
        verification_result = ai_agent.verify_task_completion(
            user_task_id, data["proof"]
        )
        if not verification_result["success"]:
            return error_response(verification_result["error"])

        response_data = {
            "verified": verification_result.get("passed", True),
            "xp_earned": verification_result.get("xp_earned", 0),
        }

        if "tokens_earned" in verification_result:
            response_data["tokens_earned"] = verification_result["tokens_earned"]

        return success_response(response_data)
    except Exception as e:
        logger.error(f"Error verifying task: {e}")
        return error_response(str(e))


# Quest system
@require_http_methods(["GET"])
def get_available_quests(request, telegram_id):
    """Get available quests from projects"""
    try:
        quests_result = ai_agent.find_relevant_quests(telegram_id)
        if quests_result["success"]:
            return success_response({"quests": quests_result["quests"]})
        return error_response(quests_result["error"])
    except Exception as e:
        logger.error(f"Error getting quests: {e}")
        return error_response(str(e))


@csrf_exempt
@require_http_methods(["POST"])
def assign_quest(request, quest_id, telegram_id):
    """Assign a project quest to user"""
    try:
        user = User.objects.get(telegram_id=telegram_id)
        quest = Task.objects.get(id=quest_id, task_type="quest")

        if user.level < quest.min_level:
            return error_response("User level too low for this quest")

        user_task = UserTask.objects.create(user=user, task=quest, status="pending")

        # Send notification
        send_telegram_notification(user.telegram_id, quest)

        return success_response(
            {"assigned": True, "task_id": user_task.id, "title": quest.title}
        )
    except (User.DoesNotExist, Task.DoesNotExist):
        return error_response("User or quest not found", 404)
    except Exception as e:
        logger.error(f"Error assigning quest: {e}")
        return error_response(str(e))


# Reward system
@csrf_exempt
@require_http_methods(["POST"])
def claim_tokens(request, telegram_id):
    """Claim accumulated token rewards"""
    try:
        user = User.objects.get(telegram_id=telegram_id)
        if not user.wallet_address:
            return error_response("User has no wallet connected")

        # Get all verified tasks with token rewards not yet claimed
        tasks = UserTask.objects.filter(
            user=user, status="verified", task__token_reward__gt=0
        ).exclude(verification_data__has_key="tokens_claimed")

        total_tokens = sum(task.task.token_reward for task in tasks)
        if total_tokens == 0:
            return error_response("No tokens to claim")

        # Send transaction
        tx_result = issue_token_reward(user.wallet_address, total_tokens)
        if not tx_result["success"]:
            return error_response("Token transfer failed")

        # Mark tasks as claimed
        for task in tasks:
            verification_data = task.verification_data or {}
            verification_data["tokens_claimed"] = True
            task.verification_data = verification_data
            task.save()

        return success_response(
            {"tx_hash": tx_result["tx_hash"], "tokens_claimed": total_tokens}
        )
    except User.DoesNotExist:
        return error_response("User not found", 404)
    except Exception as e:
        logger.error(f"Error claiming tokens: {e}")
        return error_response(str(e))


@csrf_exempt
@require_http_methods(["POST"])
def claim_nft_badge(request, telegram_id):
    """Claim NFT badge for level achievement"""
    try:
        user = User.objects.get(telegram_id=telegram_id)
        if not user.wallet_address:
            return error_response("User has no wallet connected")

        # Check if user has reached a level that qualifies for NFT
        if user.level < 3:  # Example: NFT at level 3+
            return error_response("User level too low for NFT badge")

        # Check if already claimed
        if UserTask.objects.filter(
            user=user, task__nft_reward=True, status="verified"
        ).exists():
            return error_response("NFT already claimed for this level")

        # Mint NFT
        badge_data = {
            "id": f"level_{user.level}_badge",
            "name": f"Web3 Learner Level {user.level}",
            "description": f"Awarded for reaching level {user.level}",
            "image": f"https://ipfs.io/ipfs/badges/level_{user.level}.png",
        }

        tx_result = mint_nft_badge(user.wallet_address, badge_data)
        if not tx_result["success"]:
            return error_response("NFT minting failed")

        return success_response(
            {
                "tx_hash": tx_result["tx_hash"],
                "token_uri": tx_result["token_uri"],
                "level": user.level,
            }
        )
    except User.DoesNotExist:
        return error_response("User not found", 404)
    except Exception as e:
        logger.error(f"Error claiming NFT: {e}")
        return error_response(str(e))


# Project integration
@csrf_exempt
@require_http_methods(["POST"])
def create_project_quest(request):
    """Endpoint for projects to create new quests"""
    data = get_request_data(request)
    required_fields = ["title", "description", "project", "verification_type"]

    if not data or any(field not in data for field in required_fields):
        return error_response("Missing required fields")

    try:
        # Verify project API key if needed
        # project_api_key = request.headers.get('X-Project-API-Key')
        # if not validate_project_key(project_api_key):
        #     return error_response('Invalid project key', 403)

        # Create quest
        quest = Task.objects.create(
            title=data["title"],
            description=data["description"],
            task_type="quest",
            project=data["project"],
            xp_reward=data.get("xp_reward", 50),
            token_reward=data.get("token_reward", 25),
            nft_reward=data.get("nft_reward", False),
            min_level=data.get("min_level", 1),
            verification_type=data["verification_type"],
            verification_data=data.get("verification_data", {}),
        )

        return success_response({"quest_id": quest.id, "title": quest.title})
    except Exception as e:
        logger.error(f"Error creating project quest: {e}")
        return error_response(str(e))
