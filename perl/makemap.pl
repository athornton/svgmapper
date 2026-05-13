#!/usr/bin/perl
use Getopt::Std;
our($opt_f,$opt_o,$opt_h) = ();
getopts('hf:o:');

if ($opt_h) {
    print <<EOF
$0 [-f input] [-o output] [-h] -- Make SVG map from level description file
EOF
    ;

    exit 0;
}

# Map constants
$sqtoinch = 4;
$iqs = 1/$sqtoinch;

# M is a scaling factor because font sizes don't work well with
#  fractional points

$m = 100;

# One-page template is 30x30

$gridsizex=30 * $m;
$gridsizey=30 * $m;

# Adjust so it looks nice, if this doesn't suit

$gridstroke = 0.008 * $m;
$wallstroke = 0.05 * $m;
$thickwallstroke = 0.15 * $m;
$thinstroke = 0.02 * $m;

# File that holds level data
unless ($opt_f) {
    $opt_f = "-";
}
open (INPUT,"<$opt_f") or
    die ("Could not open level data file $opt_f: $!\n");

if ($opt_o) {
    open(OUTPUT,">$opt_o") or do {
    close(INPUT);
    die("Could not open output file $filename: $!\n");
    };
    select OUTPUT;
}

# For scaling the paper.  One-page template is actually
#  six-to-the-inch, five inches square.  SVG looks better a bit bigger.

$height = $gridsizey * $iqs / $m;
$width  = $gridsizex * $iqs / $m;

$strokecolor="#1EAED0";  # TSR Blue, as near as we can figure

# Print SVG header
print <<EOF
<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd ">
<svg width="${width}in" height="${height}in" viewBox="0 0 $gridsizex $gridsizey" xmlns="http://www.w3.org/2000/svg" >
        <desc>map grid</desc>
EOF
    ;

buildlib();
drawgrid();
drawfeatures();

# Print SVG footer
print "</svg>\n";
if ($opt_o) {
    close OUTPUT;
    select STDOUT;
}

exit 0;

sub buildlib {
    # Define hatching for pits
    my $s = $m * .25;
    my $w = $m * .015;
   print <<EOF;
<defs>
    <pattern id="hatch00" patternUnits="userSpaceOnUse"
                          x="0" y="0" width="$s" height="$s"
              viewBox="0 0 $s $s">
              <g style="fill:white; stroke: $strokecolor;
                                    stroke-width:$w">
              <path d="M0,0 l$s,$s" />
                          </g>
    </pattern>
</defs>

EOF
;
}


sub drawgrid {
    my $i, $j = 0;
    for ($i=0; $i < $gridsizey; $i += $m) {
    for ($j=0; $j < $gridsizex; $j += $m) {
        print ("        <rect height=\"" . $m . "\" width=\"" . $m .
           "\" stroke=\"" . $strokecolor . "\" y=\"" . $i .
           "\" x=\"". $j . "\" stroke-width=\"" .
           $gridstroke . "\" fill=\"none\"/>\n");
    }
    }
}

sub drawfeatures {
    my $inproc = 0;
    while (<INPUT>) {
    chomp;
    s/^\s+//;
    s/\s+$//;
    # Discard comments and blank lines
    next if (/^$/);
    next if (/^#/);
    my ($kind,$startx,$starty,$endx,$endy,$type) = split(',');
    my $x1 = $startx * $m;
    my $y1 = $starty * $m;
    my $x2 = 0;
    my $y2 = 0;
    unless ($kind == 9) {
        # Text doesn't use the second coordinates, and doing math on
            #  a string is a bad idea
        $x2 = $endx * $m;
        $y2 = $endy * $m;
    }
    if ($kind == 1) {
        # Wall
        my $sw = $wallstroke;
        if (($type == 2) or ($type == 4)) {
        # Thick or dotted
        $sw=$thickwallstroke;
        }
        if ($type == 5) {
        # Thin (used for furniture)
        $sw = $thinstroke;
        }
        # Draw a wall
        print "        <line x1=\"" . $x1 . "\" y1=\"" . $y1 .
        "\" x2=\"" . $x2 . "\" y2 =\"" . $y2 . "\" " .
        "stroke = \"" . $strokecolor . "\" stroke-width=\"" . $sw .
        "\" ";
        if ($type == 3 ) { # Dashed
        print "stroke-dasharray=\"" . (0.2 * $m) . " " .
            (0.2 * $m) . "\"";
        } elsif ($type == 4) { # Dotted
        print "stroke-dasharray=\"" . (0.10 * $m) . " " .
            (0.15 * $m) . "\"";
        }
        print "/>\n";
    } elsif ($kind == 2) {
        # Arc not implemented yet
    } elsif ($kind == 3) { # Door
        my $sw = $wallstroke;
        my $h = 0.4 * $m ;
        my $w = 0.2 * $m ;
        my $x = $x1 - (0.1 * $m);
        my $y = $y1 + (0.3 * $m);
        if ($type == 2) { # Horizontal Door
        $h = (0.2 * $m);
        $w = (0.4 * $m);
        $x = $x1 + (0.3 * $m);
        $y = $y1 - (0.1 * $m);
        } elsif ($type == 3) { # Vertical Double Door
        $h = (0.3 * $m);
        $y = $y1 + (0.2 * $m);
        } elsif ($type == 4) { # Horizontal Double Door
        $h = 0.2 * $m;
        $w = 0.3 * $m;
        $x = $x1 + (0.2 * $m);
        $y = $y1 - (0.1 * $m);
        }
        print ("        <rect height=\"" . $h . "\" width=\"" . $w .
           "\" stroke=\"" . $strokecolor . "\" y=\"" . $y .
           "\" x=\"". $x . "\" stroke-width=\"" .
           $sw . "\" fill=\"white\"/>\n");

        if (($type == 3) or ($type == 4)) {
        if ($type == 3) {
            $y = $y + (0.3 * $m);
        } elsif ($type == 4) {
            $x = $x + ( 0.3 * $m);
        }
        print ("        <rect height=\"" . $h . "\" width=\"" . $w .
           "\" stroke=\"" . $strokecolor . "\" y=\"" . $y .
           "\" x=\"". $x . "\" stroke-width=\"" .
           $sw . "\" fill=\"white\"/>\n");
        }
    } elsif ($kind == 5) { # Polygon
        my $sw=$wallstroke;
        if ($type > 4) {
        $sw=$thinstroke;
        $type = $type - 4;
        }
        if ($type == 1) {
        $fill = $strokecolor;
        } elsif ($type == 2) {
        $fill = "white";
        } elsif ($type == 3) {
        $fill = "url(#hatch00)";
        }
        # Start a polygon
        $inproc=1;
        print "         <polygon fill=\"" . $fill .
        "\" stroke=\"" . $strokecolor . "\" stroke-width=\"" .
        $sw . "\" ";
        if ($type == 3) {
        print " stroke-dasharray=\"" . (0.08 * $m) . " " .
            (0.08 * $m) . "\" ";
        }
        print " points = \"" .
        $x1 . "," . $y1 . "   " . $x2 . "," . $y2 . "   ";
    } elsif (($kind == 99) and ($inproc == 1)) {
        # Continue a polygon
        print $x2 . "," . $y2 . "   ";
        if ($type == 99) {
        $inproc = 0;
        # Close path
        print "\" />\n";
        }
    } elsif ($kind == 6) { # Filled ellipse
        my $cx=$x1;
        my $cx=$y1;
        my $rx=$x2;
        my $ry=$y2;
        my $sw=$wallstroke;
        if ($type > 4) {
        $sw = $thinstroke;
        $type = $type - 4;
        }
        if ($type == 1) {
        $fill = $strokecolor;
        } elsif ($type == 2) {
        $fill = "white";
        } elsif ($type == 3) {
        $fill = "url(#hatch00)";
        }
        print "         <ellipse fill=\"" . $fill .
        "\" stroke=\"" . $strokecolor . "\" stroke-width=\"" .
        $sw . "\" cx=\"" .
        $x1 . "\" cy=\"" . $y1 . "\" rx=\"". $x2 . "\" ry=\"" . $y2 .
        "\" />\n";
    } elsif ($kind == 7) { # Spiral Stairs
        my $z=(sqrt(2)/4) * $m;  # For diagonals
        $sw = (($wallstroke + $thinstroke) / 2);
                print "        <circle fill=\"white\" stroke=\"" .
        $strokecolor ."\" stroke-width=\"" . $sw .
        "\" cx=\"" . $x1 . "\" cy=\"" . $y1 . "\" r=\"".
        .5 * $m . "\" />\n";
        print "        <line stroke=\"" . $strokecolor .
        "\" stroke-width=\"" . $sw . "\" y1=\"" .
        ($y1 + 0.5 * $m) .
        "\" x1=\"" . $x1 . "\" y2=\"" .
        ($y1 - 0.5 * $m) .
        "\" x2=\"" . $x1 . "\" />\n";
        print "        <line stroke=\"" . $strokecolor .
        "\" stroke-width=\"" . $wallstroke . "\" x1=\"" .
        ($x1 + 0.5 * $m) .
        "\" y1=\"" . $y1 . "\" x2=\"" .
        ($x1 - 0.5 * $m) .
        "\" y2=\"" . $y1 . "\" />\n";
        print "        <line stroke=\"" . $strokecolor .
        "\" stroke-width=\"" . $wallstroke . "\" x1=\"" . ($x1 + $z) .
        "\" y1=\"" . ($y1 - $z) . "\" x2=\"" . ($x1 - $z) .
        "\" y2=\"" . ($y1 + $z) . "\" />\n";
        print "        <line stroke=\"" . $strokecolor .
        "\" stroke-width=\"" . $wallstroke . "\" x1=\"" . ($x1 + $z) .
        "\" y1=\"" . ($y1 + $z) . "\" x2=\"" . ($x1 - $z) .
        "\" y2=\"" . ($y1 - $z) . "\" />\n";
    } elsif ($kind == 8) { # Toilets.  Hey, they're a common feature
        my $cx=$x1;
        my $cy=$y1;
        my $sw=$thinstroke;
        my $rx=0.15 * $m;
        my $ry=0.2 * $m;
        my $drainsize = 0.03 * $m;
        $fill = "white";
        if ($kind == 2) {
        $rx=0.2 * $m;
        $ry=0.15 * $m;
        }
        print "         <ellipse fill=\"" . $fill .
        "\" stroke=\"" . $strokecolor . "\" stroke-width=\"" .
        $sw . "\" cx=\"" .
        $cx . "\" cy=\"" . $cy . "\" rx=\"". $rx . "\" ry=\"" . $ry .
        "\" />\n";
        if ($kind == 1) {
        $cy = $cy - (0.05 * $m);
        } elsif ($kind == 2) {
        $cx = $cx - (0.05 * $m);
        }
        print "         <circle fill=\"" . $strokecolor . "\" stroke=\"" .
        $strokecolor . "\" stroke-width=\"" . $thinstroke .
        "\" cx=\"" . $cx . "\" cy=\"" . $cy . "\" r=\"" .
        $drainsize . "\" />\n";


    } elsif ($kind == 9) { # Text
        my $text=$endx;
        my $tstyle=$endy;
        my $size=$type * $m;
        my $font="HelveticaNeue-CondensedBold";
            # Close to fonts used in Classic AD&D V1: S1-3, G1-3, A1-4, etc.
        my $ffamily = "sans-serif";
        if ($tstyle eq "s") {
        $font="Soutane"; # Close to X3-X4 font
        $ffamily = "serif";
        }
        print "        <text x=\"" . $x1 . "\" y=\"" . $y1 .
        "\" style=\"font-family: " . $font . ","
        . $ffamily .";" .
        "stroke: " . $strokecolor . "; " .
        "font-size: " . $size . "; " .
        "stroke-width: " . $thinstroke . "; " .
        "fill: " . $strokecolor . ";\">" . $text .
        "</text>\n";
    } else {
        # Unknown feature
    }
    }
    close(INPUT);
}
