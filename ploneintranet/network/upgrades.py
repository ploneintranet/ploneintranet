default_profile = 'profile-plonesocial.network:default'


def upgrade_to_0002(context):
    context.runImportStepFromProfile(default_profile, 'componentregistry')
