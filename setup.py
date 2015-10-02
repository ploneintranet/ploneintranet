from setuptools import setup, find_packages

version = '1.0b1'

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='ploneintranet',
      version=version,
      description='Intranet suite for Plone',
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Plone',
          'Framework :: Plone :: 5.0',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Office/Business',
          'Topic :: Office/Business :: Groupware',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ],
      keywords='intranet social activitystream collaboration groupware',
      author='Plone Intranet Consortium',
      author_email='info@ploneintranet.org',
      url='https://github.com/ploneintranet/ploneintranet',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.instancebehavior',
          'requests',
          'loremipsum',
          'z3c.jbot',
          'plone.tiles',
          'plone.app.tiles',
          'plone.app.async',
          'plone.app.blocks',
          'plone.app.theming',
          'BeautifulSoup',
          'mincemeat',
          'networkx',
          'rwproperty',
          'collective.z3cform.chosen',
          'dexterity.membrane',
          'Plone',
          'plone.api',
          'Products.UserAndGroupSelectionWidget',
          'plone.directives.form',
          'plone.directives.dexterity',
          'plone.principalsource',
          'collective.documentviewer',
          'collective.workspace',
          'fake-factory',
          'Celery[redis]',
          'redis',
          'pathlib',
          'collective.externaleditor >= 1.0.2',
          'tablib',
          'collective.dexteritytextindexer',
          'twitter-text-python',
          'Unidecode',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.app.robotframework[debug]',
              'fake-factory',
              'mock',
              'responses',
          ],
          'socialsuite': [
              'loremipsum',
          ],
          'suite': [
              'requests',
              'plone.tiles',
              'plone.app.blocks',
          ],
          'core': [
              'plone.app.tiles',
          ],
          'microblog': [
              'requests',
              'plone.tiles',
              'plone.app.tiles',
          ],
          'activitystream': [
              'plone.app.blocks',
          ],
          'pagerank': [
              'requests',
              'plone.tiles',
              'plone.app.blocks',
          ],
          'themeswitcher': [
              'plone.app.theming',
          ],
          'todo': [
              'rwproperty',
              'plone.directives.dexterity',
              'plone.principalsource',
          ],
          'docconv': [
              'slc.docconv',
              'plone.async',
              'BeautifulSoup',
          ],
          'pagerank': [
              'networkx',
              'mincemeat',
          ],
          'attachments': [
              'Products.UserAndGroupSelectionWidget'
          ],
          'develop': ['plone.reload', 'iw.debug', 'i18ndude'],
          'release': [
              'zest.releaser',
              'check-manifest',
              'pyroma',
              'zest.pocompile',
              'gocept.zestreleaser.customupload',
              'twine',
          ],
          'solr': [
              'collective.indexing >= 2.0a2',
              'requests',
              'scorched',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone

      [zest.releaser.releaser.after_checkout]
      add_files_to_release = ploneintranet.core.release:add_files_to_release
      """)
