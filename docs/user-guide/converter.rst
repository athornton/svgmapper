#####################################
Converting old-style map descriptions
#####################################

The original `makemap`_ used a six-column format where each object kind, coordinate, and object type was represented numerically.

SVGMapper also uses a six-column format, but the object kind and type have been replaced by human-readable words.

``svgmapper convert`` can be used to translate the old format into the new format.

.. _makemap: ../perl/makemap.pl
