#!/usr/bin/perl
 
use 5.010;
use strict;
 
use Getopt::Long 0 qw(:config permute bundling no_auto_abbrev);
use HTML::HTML5::Parser 0.107 qw();
use HTML::HTML5::Sanity 0.101 qw(fix_document);
use XML::LibXML::PrettyPrint 0.001 qw();
use HTML::HTML5::Writer 0.104 qw();
 
# Read command-line options
my %options;
Getopt::Long::GetOptions(\%options,
  'markup|m=s',
  'polyglot=i',
  'doctype=s',
  'charset=s',
  'quote_attributes=s',
  'voids=s',
  'start_tags=s',
  'end_tags=s',
  'refs=s',
  'indent_string=s',
  );
my $input  = shift // '-';
my $output = shift // '-';
 
# Create a parser object and parse input HTML
my $parser = HTML::HTML5::Parser->new;
my $dom = ($input eq '-')
  ? $parser->parse_string(do { local $/ = <STDIN> })
  : $parser->parse_file($input);
 
# Use HTML::HTML5::Sanity to fix up HTML quirks
$HTML::HTML5::Sanity::FIX_LANG_ATTRIBUTES = 2;
my $fixed_dom = fix_document($dom);
 
# Pretty indentation
XML::LibXML::PrettyPrint
  ->new_for_html(indent_string => (delete $options{indent_string} // "\t"))
  ->pretty_print($fixed_dom);
 
# Create a writer object
my $writer = HTML::HTML5::Writer
  ->new(%options);
 
if ($output eq '-')
{
  # Output to STDOUT
  say $writer->document($fixed_dom);
}
else
{
  # Output to FILE
  open my($fh), '>:encoding(UTF-8)', $output;
  say $fh $writer->document($fixed_dom);
  close $fh;
}
