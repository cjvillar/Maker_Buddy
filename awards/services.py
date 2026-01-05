from awards.models import Award, UserAward

# services connects the award rule to the db


def evaluate_awards(user, rules_to_check):
    # takes list of rule classes and adds to db if eligible.

    for rule_class in rules_to_check:
        if rule_class.is_eligible(user):
            # ret tuple (award_obj, bool)
            award = Award.objects.get_or_create(
                code=rule_class.code,
                defaults={
                    "name": rule_class.name,
                    "description": rule_class.description,
                },
            )
            # pass award_obj to UserAward
            award_obj = award[0]
            UserAward.objects.get_or_create(user=user, award=award_obj)
