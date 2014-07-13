require 'compass/import-once/activate'
# Require any additional compass plugins here.

# Set this to the root of your project when deployed:
http_path = "/"
css_dir = "style"
sass_dir = "_sass"
images_dir = "style"
javascripts_dir = "lib"
fonts_dir = "style"
environment = :development
# environment = :production
# In development, we can turn on the FireSass-compatible debug_info.
firesass = false
# firesass = true

output_style = :nested

# To enable relative paths to assets via compass helper functions. Uncomment:
# relative_assets = true

# To disable debugging comments that display the original location of your selectors. Uncomment:
# line_comments = false
color_output = false

# You can select your preferred output style here (can be overridden via the command line):
# output_style = :expanded or :nested or :compact or :compressed
output_style = (environment == :development) ? :expanded : :compressed

# To use relative paths to assets in your compiled CSS files, set this to true.
relative_assets = true


# To disable debugging comments that display the original location of your selectors. Uncomment:
line_comments = false


# Pass options to sass. For development, we turn on the FireSass-compatible
# debug_info if the firesass config variable above is true.
sass_options = (environment == :development && firesass == true) ? {:debug_info => true} : {}


