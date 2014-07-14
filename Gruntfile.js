module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    uglify: {
      build: {
        src: 'bundle.js',
        dest: 'bundle.min.js'
      }
    },
    autoprefixer: {
      dist: {
        options: {
          browsers: ['> 1%', 'last 4 versions', 'Firefox ESR', 'Opera 12.1']
        },
        src: 'prototype/style/base.css',
        dest: 'prototype/_site/style/base.css'
      }
    },
    cssmin: {
      combine: {
        files: {
            'prototype/_site/style/base.css': ['prototype/_site/style/base.css']
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-autoprefixer');

  // Default task(s).
  grunt.registerTask('default', ['uglify']);
  grunt.registerTask('css', ['autoprefixer', 'cssmin']);

};
