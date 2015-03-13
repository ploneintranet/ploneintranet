default_profile = 'profile-ploneintranet.network:default'


def upgrade_to_0002(context):
    context.runImportStepFromProfile(default_profile, 'componentregistry')
