from django.db import models


class User(models.Model):
    """User profile data"""

    telegram_id = models.CharField(max_length=50, unique=True)
    wallet_addresses = models.JSONField(
        default=dict
    )  # {'gnosis': '0x...', 'rootstock': '0x...'}
    preferred_chain = models.CharField(max_length=20, default="gnosis")
    xp_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    interests = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.telegram_id} (Level {self.level})"


class LearningPath(models.Model):
    """Personalized learning path for a user"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="learning_paths"
    )
    topic = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("completed", "Completed"),
            ("paused", "Paused"),
        ],
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.topic} Path"


class Task(models.Model):
    """Learning tasks and quests"""

    TYPES = [
        ("learning", "Learning"),
        ("practice", "Practice"),
        ("quest", "Quest"),
        ("advanced", "Advanced"),
    ]

    STATUS = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("verified", "Verified"),
        ("failed", "Failed"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    task_type = models.CharField(max_length=20, choices=TYPES)
    xp_reward = models.IntegerField(default=0)
    token_reward = models.IntegerField(default=0)
    nft_reward = models.BooleanField(default=False)
    min_level = models.IntegerField(default=1)
    verification_type = models.CharField(max_length=50)
    verification_data = models.JSONField(default=dict)
    project = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    supported_chains = models.JSONField(default=list)  # ['gnosis', 'rootstock']
    chain_specific_data = models.JSONField(default=dict)
    olas_service_id = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.task_type})"


class UserTask(models.Model):
    """User's assigned tasks"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_tasks")
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=Task.STATUS, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    verification_data = models.JSONField(default=dict)
    reward_chain = models.CharField(max_length=20, null=True, blank=True)
    reward_tx_hash = models.CharField(max_length=66, null=True, blank=True)
    verified_by_olas = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.task}"
