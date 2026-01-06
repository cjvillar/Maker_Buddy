# checks if user or project can get the award: True False


class BaseAwardRule:
    code = None

    @classmethod
    def get_project_model(cls):
        # helper to avoid circular imports
        from maker_projects.models import MakerProject

        return MakerProject

    @classmethod
    def is_eligible(cls, user):
        raise NotImplementedError


class FirstProjectAward(BaseAwardRule):
    code = "first_project_complete"
    name = "Completed First Project"
    description = "You finished your first project. Welcome to the maker community!"

    @classmethod
    def is_eligible(cls, user):
        MakerProject = cls.get_project_model()
        return user.maker_projects.filter(status=MakerProject.Status.COMPLETED).exists()


# award registry
PROJECT_AWARDS = [FirstProjectAward]
ACTIVITY_AWARDS = []  # will add user activity awards when I make them up

ALL_AWARDS = PROJECT_AWARDS + ACTIVITY_AWARDS
