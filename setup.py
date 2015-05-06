from setuptools import setup, find_packages

version = '0.1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='ploneintranet',
      version=version,
      description="Intranet suite for Plone",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      ],
      keywords='',
      author='',
      author_email='',
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
          'requests',
          'loremipsum',
          'slc.docconv',
          'z3c.jbot',
          'plone.tiles',
          'plone.app.tiles',
          'plone.app.async',
          'plone.app.blocks',
          'BeautifulSoup',
          'mincemeat',
          'networkx',
          'rwproperty',
          'collective.z3cform.chosen',
          'Plone',
          'plone.api',
          'Products.UserAndGroupSelectionWidget',
          'plone.directives.form',
          'plone.directives.dexterity',
          'plone.principalsource',
          'collective.celery',
          'collective.workspace',
          'fake-factory',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.app.robotframework[debug]',
              'fake-factory',
              'plonesocial.suite',
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
          'simplesharing': [
              'collective.z3cform.chosen',
              'plone.directives.form',
          ],
          'pagerank': [
              'networkx',
              'mincemeat',
          ],
          'attachments': [
              'Products.UserAndGroupSelectionWidget'
          ],
          'develop': ['plone.reload', 'iw.debug'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
