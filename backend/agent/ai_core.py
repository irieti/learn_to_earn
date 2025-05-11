import os
import json
import logging
import openai
from datetime import datetime
from .models import User, Task, UserTask, LearningPath
from .views import send_telegram_notification

logger = logging.getLogger(__name__)


class LearnEarnAIAgent:
    """Core AI agent for the Learn & Earn platform"""

    def __init__(self):
        """Initialize the AI agent"""
        # Get OpenAI API key from environment
        self.openai_api_key = os.environ.get("CONNECTION_CONFIGS_CONFIG_OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
        else:
            openai.api_key = self.openai_api_key

    def generate_ai_task(self, user, topic=None, task_type="learning"):
        """Auto-create a task matching user's level and interests"""
        if not topic:
            topic = list(user.interests.keys())[0]  # Use primary interest

        prompt = f"""
    Create a {task_type} task about {topic} for a Web3 learner (Level {user.level}).
    Format as JSON with:
    - title: Max 8 words
    - description: 1-2 sentences
    - verification_type: quiz/transaction/social_proof
    - xp_reward: {10 * user.level} to {20 * user.level}
    - token_reward: Half of XP value
        {"" if task_type != "quest" else "- project: 'AI Generated'"}
    
        Example for Level 1 DeFi:
        {{
        "title": "What is a DEX?",
        "description": "Explain how decentralized exchanges work in 2 sentences.",
        "verification_type": "quiz",
        "xp_reward": 15,
        "token_reward": 7
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        task_data = json.loads(response.choices[0].message.content)
        return self._save_ai_task(user, task_data, task_type)

    def _save_ai_task(self, user, task_data, task_type):
        """Save generated task to DB"""
        task = Task.objects.create(
            title=task_data["title"],
            description=task_data["description"],
            task_type=task_type,
            xp_reward=task_data["xp_reward"],
            token_reward=task_data.get("token_reward", task_data["xp_reward"] // 2),
            verification_type=task_data["verification_type"],
            min_level=user.level,
            verification_data=self._generate_verification_data(task_data),
        )
        return task

    def _generate_verification_data(self, task_data):
        """Create quiz questions or verification rules"""
        if task_data["verification_type"] == "quiz":
            prompt = f"""
            Generate 3 multiple-choice questions about:
            {task_data['title']} - {task_data['description']}
            Format as JSON with 'questions' array containing:
            - question: String
            - options: Array of 4 strings
            - correct_answer: String (exact option text)
            """
            response = openai.ChatCompletion.create(...)
            return json.loads(response.choices[0].message.content)
        return {}  # Other types handled during verification

    def create_personalized_path(self, user_id, interest):
        """Create a personalized learning path with AI-generated tasks"""
        try:
            user = User.objects.get(telegram_id=user_id)

            # Create learning path container
            learning_path = LearningPath.objects.create(
                user=user, topic=interest, status="active"
            )

            # Generate progressive tasks
            task_types = ["learning", "practice", "quest"]  # Basic progression
            generated_tasks = []

            for i, task_type in enumerate(task_types):
                # Scale difficulty based on position in path
                difficulty = {
                    "learning": "beginner",
                    "practice": "intermediate",
                    "quest": "advanced",
                }[task_type]

                # Generate task
                task = self.generate_ai_task(
                    user=user,
                    topic=interest,
                    task_type=task_type,
                    difficulty=difficulty,
                )

                # Connect to path
                UserTask.objects.create(
                    user=user,
                    task=task,
                    learning_path=learning_path,
                    status="pending",
                    order=i + 1,  # Track progression order
                )

                # Send notification for quests only
                if task_type == "quest":
                    send_telegram_notification(user.telegram_id, task)

                generated_tasks.append(task)

            # Generate path description using GPT
            path_description = self._generate_path_description(
                interest=interest, tasks=generated_tasks, user_level=user.level
            )

            learning_path.description = path_description
            learning_path.save()

            return {
                "success": True,
                "path_id": learning_path.id,
                "tasks": [
                    {"id": t.id, "title": t.title, "type": t.task_type}
                    for t in generated_tasks
                ],
            }

        except Exception as e:
            logger.error(f"Path creation failed: {e}")
            return {"success": False, "error": str(e)}

    def _generate_path_description(self, interest, tasks, user_level):
        """Generate human-readable path overview"""
        prompt = f"""Summarize this {interest} learning path (Level {user_level}) in 2 sentences.
        Tasks:
        {chr(10).join(f"- {t.task_type}: {t.title}" for t in tasks)}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Faster for descriptions
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        return response.choices[0].message.content

    def verify_task_completion(self, user_task_id, proof_data):
        """Verify if a task has been completed based on proof data"""
        try:
            user_task = UserTask.objects.get(id=user_task_id)
            task = user_task.task

            # Different verification logic based on verification type
            if task.verification_type == "quiz":
                return self._verify_quiz(user_task, proof_data)
            elif task.verification_type == "transaction":
                return self._verify_transaction(user_task, proof_data)
            elif task.verification_type == "social_proof":
                return self._verify_social_proof(user_task, proof_data)
            elif task.verification_type == "submission":
                return self._verify_submission(user_task, proof_data)
            else:
                return {"success": False, "error": "Unknown verification type"}

            if success and random() < 0.3:  # 30% chance to suggest new task
                user = UserTask.objects.get(id=user_task_id).user
                new_task = self.generate_ai_task(user)
                # Send via Telegram: "Try this next: {new_task.title}"

        except UserTask.DoesNotExist:
            return {"success": False, "error": "Task not found"}
        except Exception as e:
            logger.error(f"Error verifying task: {e}")
            return {"success": False, "error": str(e)}

    def _verify_quiz(self, user_task, proof_data):
        """Verify quiz answers"""
        correct_answers = user_task.task.verification_data.get("answers", {})
        user_answers = proof_data.get("answers", {})

        score = 0
        total = len(correct_answers)

        for question, correct_answer in correct_answers.items():
            if question in user_answers and user_answers[question] == correct_answer:
                score += 1

        # Update user's progress
        if score / total >= 0.7:  # 70% to pass
            user_task.status = "verified"
            user_task.completed_at = datetime.now()
            user_task.verification_data = {"score": score, "total": total}
            user_task.save()

            # Update user XP
            user = user_task.user
            user.xp_points += user_task.task.xp_reward

            # Check if user level up is needed
            new_level = self._calculate_level(user.xp_points)
            if new_level > user.level:
                user.level = new_level

            user.save()

            return {
                "success": True,
                "passed": True,
                "score": f"{score}/{total}",
                "xp_earned": user_task.task.xp_reward,
                "level_up": new_level > user.level,
            }
        else:
            user_task.status = "failed"
            user_task.verification_data = {"score": score, "total": total}
            user_task.save()
            return {"success": True, "passed": False, "score": f"{score}/{total}"}

    def _verify_transaction(self, user_task, proof_data):
        """Verify blockchain transaction proof"""
        tx_hash = proof_data.get("transaction_hash")
        if not tx_hash:
            return {"success": False, "error": "No transaction hash provided"}

        # Use web3 to verify the transaction
        # This is a simplified placeholder - real implementation would check chain
        from .blockchain import verify_transaction_on_chain

        verification = verify_transaction_on_chain(
            tx_hash, user_task.task.verification_data.get("requirements", {})
        )

        if verification["verified"]:
            # Update user task
            user_task.status = "verified"
            user_task.completed_at = datetime.now()
            user_task.verification_data = {"tx_hash": tx_hash}
            user_task.save()

            # Update user XP and tokens
            user = user_task.user
            user.xp_points += user_task.task.xp_reward

            # Update level if needed
            new_level = self._calculate_level(user.xp_points)
            if new_level > user.level:
                user.level = new_level

            user.save()

            # Issue token reward if needed
            if user_task.task.token_reward > 0:
                from .blockchain import issue_token_reward

                issue_token_reward(user.wallet_address, user_task.task.token_reward)

            return {
                "success": True,
                "xp_earned": user_task.task.xp_reward,
                "tokens_earned": user_task.task.token_reward,
                "level_up": new_level > user.level,
            }
        else:
            return {"success": False, "error": verification["reason"]}

    def _verify_social_proof(self, user_task, proof_data):
        """Verify social media interaction proof"""
        # For MVP: Simple verification with screenshot or link
        proof_link = proof_data.get("proof_link")

        if not proof_link:
            return {"success": False, "error": "No proof provided"}

        # Ask GPT to verify the proof (social media post, etc.)
        prompt = f"""
        Verify this social proof for a Web3 task completion:
        Task: {user_task.task.title}
        Requirement: {user_task.task.description}
        Provided proof: {proof_link}
        
        Is this valid proof of task completion? Answer only YES or NO and explain briefly why.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are verifying task completion evidence.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        verification_result = response.choices[0].message.content
        is_verified = "YES" in verification_result.upper().split()

        if is_verified:
            # Update user task
            user_task.status = "verified"
            user_task.completed_at = datetime.now()
            user_task.verification_data = {
                "proof": proof_link,
                "ai_verification": verification_result,
            }
            user_task.save()

            # Update user XP
            user = user_task.user
            user.xp_points += user_task.task.xp_reward

            # Check if user level up is needed
            new_level = self._calculate_level(user.xp_points)
            if new_level > user.level:
                user.level = new_level

            user.save()

            return {
                "success": True,
                "xp_earned": user_task.task.xp_reward,
                "level_up": new_level > user.level,
            }
        else:
            return {
                "success": False,
                "error": "Proof verification failed",
                "details": verification_result,
            }

    def _verify_submission(self, user_task, proof_data):
        """Verify text/code submission"""
        submission = proof_data.get("submission")

        if not submission:
            return {"success": False, "error": "No submission provided"}

        # Ask GPT to verify the submission
        prompt = f"""
        Evaluate this submission for a Web3 task:
        Task: {user_task.task.title}
        Requirements: {user_task.task.description}
        
        User Submission:
        ```
        {submission}
        ```
        
        Score this submission from 0-10 and explain your reasoning.
        Format response as: SCORE: X/10. FEEDBACK: Your detailed feedback here.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Web3 educator evaluating submissions.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        evaluation = response.choices[0].message.content
        score_part = evaluation.split(".")[0]

        try:
            score = int(score_part.split(":")[1].strip().split("/")[0])
            passed = score >= 7  # 7/10 to pass

            if passed:
                # Update user task
                user_task.status = "verified"
                user_task.completed_at = datetime.now()
                user_task.verification_data = {
                    "submission": submission,
                    "evaluation": evaluation,
                }
                user_task.save()

                # Update user XP
                user = user_task.user
                user.xp_points += user_task.task.xp_reward

                # Check if user level up is needed
                new_level = self._calculate_level(user.xp_points)
                if new_level > user.level:
                    user.level = new_level

                user.save()

                return {
                    "success": True,
                    "passed": True,
                    "score": score,
                    "feedback": evaluation,
                    "xp_earned": user_task.task.xp_reward,
                    "level_up": new_level > user.level,
                }
            else:
                user_task.status = "failed"
                user_task.verification_data = {
                    "submission": submission,
                    "evaluation": evaluation,
                }
                user_task.save()

                return {
                    "success": True,
                    "passed": False,
                    "score": score,
                    "feedback": evaluation,
                }
        except Exception as e:
            logger.error(f"Error parsing evaluation score: {e}")
            return {"success": False, "error": "Failed to evaluate submission"}

    def _calculate_level(self, xp):
        """Calculate user level based on XP"""
        # Simple level calculation: every 100 XP is a level up
        return max(1, xp // 100 + 1)

    def find_relevant_quests(self, user_id, count=3):
        """Find relevant quests from projects based on user profile"""
        try:
            user = User.objects.get(telegram_id=user_id)

            # For MVP, simply return quests appropriate for user level
            available_quests = Task.objects.filter(
                task_type="quest", min_level__lte=user.level
            ).order_by("-created_at")[:count]

            return {
                "success": True,
                "quests": [
                    {
                        "id": quest.id,
                        "title": quest.title,
                        "description": quest.description,
                        "project": quest.project,
                        "xp_reward": quest.xp_reward,
                        "token_reward": quest.token_reward,
                        "has_nft": quest.nft_reward,
                    }
                    for quest in available_quests
                ],
            }
        except User.DoesNotExist:
            return {"success": False, "error": "User not found"}
        except Exception as e:
            logger.error(f"Error finding quests: {e}")
            return {"success": False, "error": str(e)}

    def generate_lesson_content(self, task_id):
        """Generate interactive lesson content for learning tasks"""
        try:
            task = Task.objects.get(id=task_id)

            if task.task_type != "learning":
                return {"success": False, "error": "Not a learning task"}

            # Ask GPT to generate an interactive lesson
            prompt = f"""
            Create an interactive Web3 lesson on:
            Topic: {task.title}
            
            Requirements:
            1. Explain {task.title} in a beginner-friendly way
            2. Include 3-5 key concepts
            3. Add 2-3 real-world examples
            4. End with a short 3-question quiz to test knowledge
            
            Format as markdown with clear sections.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Web3 educator."},
                    {"role": "user", "content": prompt},
                ],
            )

            lesson_content = response.choices[0].message.content

            # Generate quiz for verification
            quiz_prompt = f"""
            Based on the lesson about {task.title}, create a JSON object with 3 multiple-choice questions.
            Format:
            {{
                "questions": [
                    {{
                        "question": "The question text",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "The correct option exact text"
                    }}
                ]
            }}
            """

            quiz_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are creating a Web3 quiz."},
                    {"role": "user", "content": quiz_prompt},
                ],
            )

            quiz_content = quiz_response.choices[0].message.content
            quiz_data = json.loads(quiz_content)

            # Update task with verification data
            answers = {}
            for i, q in enumerate(quiz_data["questions"]):
                answers[f"q{i+1}"] = q["correct_answer"]

            task.verification_data = {
                "questions": quiz_data["questions"],
                "answers": answers,
            }
            task.save()

            return {
                "success": True,
                "lesson": lesson_content,
                "quiz": quiz_data["questions"],
            }

        except Task.DoesNotExist:
            return {"success": False, "error": "Task not found"}
        except Exception as e:
            logger.error(f"Error generating lesson: {e}")
            return {"success": False, "error": str(e)}
