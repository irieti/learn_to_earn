from django.urls import path
from . import views
from django.utils.timezone import now

urlpatterns = [
    # System endpoints
    path("health-check/", views.health_check, name="health_check"),
    # User onboarding and management
    path("user/onboard/", views.onboard_user, name="onboard_user"),
    path(
        "user/profile/<str:telegram_id>/",
        views.get_user_profile,
        name="get_user_profile",
    ),
    # Wallet management
    path("wallet/update/", views.update_wallet, name="update_wallet"),
    # Learning paths
    path(
        "learning/paths/create/", views.start_learning_path, name="create_learning_path"
    ),
    path(
        "learning/paths/user/<str:telegram_id>/",
        views.get_user_paths,
        name="get_user_paths",
    ),
    # Task management
    path(
        "tasks/current/<str:telegram_id>/",
        views.get_current_task,
        name="get_current_task",
    ),
    path("tasks/start/<int:user_task_id>/", views.start_task, name="start_task"),
    path("tasks/verify/<int:user_task_id>/", views.verify_task, name="verify_task"),
    # Quest system
    path(
        "quests/available/<str:telegram_id>/",
        views.get_available_quests,
        name="get_available_quests",
    ),
    path(
        "quests/assign/<int:quest_id>/<str:telegram_id>/",
        views.assign_quest,
        name="assign_quest",
    ),
    # Reward system
    path(
        "rewards/tokens/claim/<str:telegram_id>/",
        views.claim_tokens,
        name="claim_tokens",
    ),
    path(
        "rewards/nft/claim/<str:telegram_id>/", views.claim_nft_badge, name="claim_nft"
    ),
    # Project integration
    path(
        "projects/quests/create/",
        views.create_project_quest,
        name="create_project_quest",
    ),
    # Additional endpoints from original spec (if needed)
    path(
        "tasks/content/<int:task_id>/", views.get_task_content, name="get_task_content"
    ),
    path(
        "learning/paths/<int:path_id>/",
        views.get_learning_path,
        name="get_learning_path",
    ),
]
