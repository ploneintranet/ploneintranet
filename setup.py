from setuptools import setup, find_packages

version = '0.1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='ploneintranet.suite',
      version=version,
      description="Pre-integrated Intranet suite for Plone",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='',
      author_email='',
      url='https://github.com/ploneintranet/ploneintranet.suite',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ploneintranet', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Plone',
          'collective.celery',
          'ploneintranet.simplesharing',
          'ploneintranet.workspace',
          'ploneintranet.theme',
          'ploneintranet.documentviewer',
          'ploneintranet.invitations',
          'ploneintranet.docconv.client',
          'ploneintranet.attachments',
          'ploneintranet.todo',
          'ploneintranet.notifications',
          'plonesocial.microblog',
          'plonesocial.activitystream',
          'plonesocial.network',
          'plonesocial.messaging',
          'plonesocial.core',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.app.robotframework',
          ],
          'develop': [
              # 'Sphinx',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
