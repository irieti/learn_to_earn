def generate_mission():
    # Простая заглушка, потом можно подключить OpenAI или Olas SDK
    from .models import Mission

    mission, _ = Mission.objects.get_or_create(
        title="Complete a lesson on Web3 Security",
        url="https://example.com/lesson/security",
        reward="🎓 10 XP",
    )
    return mission
