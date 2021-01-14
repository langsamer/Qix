# Outline of the game cycle

1. update positions
2. check for collisions
    + Player (Stix) vs. boundary ==> close area and score
    + Player (Stix) vs. Qix ==> lose a life
    + Sparx or Fuse vs. Player (position) ==> lose a life
3. commit move


## Update positions

### move on boundary

### move off boundary
+ create Stix

### move in open area
+ update Stix

### move onto boundary
+ clamp to boundary

### move onto Stix
+ not allowed: abandon move

### Standstill
+ start fuse timer
  - need event START_FUSE
  - need timer for fuse


## Collisions

### move onto boundary
+ Close area: Post Event `CLOSE_AREA` with coordinates

### collide with Stix
+ Lose a life


## Closing Areas (and Scoring)

Indicated by event `CLOSE_AREA`

1. Find out which part(s) of the playing field contain(s) Qix
   + if one part has no Qix, close this
   + if both parts have Qix, close the smaller area (Area measurement)
   
2. Determine the appropriate orientation of the current Stix for splitting the 
   current boundary.
   This decides which of the first and second return value of Polygon.split() is the 
   closed area and which is the open area. The open area will be the new boundary.

3. Closing the polygon requires tracing along the boundary to the starting point.
   Luckily, we have Polygon.split(): When we insert the start and end point of the 
   Stix in the boundary polygon, we only need to split() the boundary by the Stix.

### Where is Qix?

Since Qix will destroy Stix on collision, Qix cannot cross the Stix polyline. Also, Qix 
cannot cross the boundary. Hence, any point of Qix suffices to determine whether Qix is 
inside a polygon defined by Stix and boundary.

+ Use [crossing number](http://www.geomalgorithms.com/a03-_inclusion.html)
   Note: only horizontal edges can cause a problem, there are no corners that the ray could touch.

### Measuring Areas

#### Use multiple counting

We walk the closed polygon in clockwise direction.
For each vertical segment,

+ we add the area to the right of it 
+ we subtract the area to the left of it

When we have completed the polygon, the sum is twice the area inside the polygon.

#### Why this works

When we are at the leftmost edge, walking up, we subtract the open area to the left of that edge.
At the same time we are adding not only inside area but also the open area to the right of the polygon.
However, that area is subtracted once we walk down along the rightmost edge. (In that direction, the
open space on the right of the polygon is to the left.) At the same time, we are adding open area left
of the polygon - just what we subtracted when we were walking up on the left.

It may take a bit of thinking to understand that this also works for non-convex shapes.
This method always counts the inside parts twice while the outside parts cancel out.

An example in 1 dimension: two intervals on the number line (the plus signs only mark the intervals, 
they are meant as zero-width points)

    |-+==+--+====+----|
    0 a  b  c    d    13

When you switch from the left edge of an interval to 
the right edge of an interval (same or different), you must switch sign - which stands for walking 
up or down in the 2D version.

No matter whether you walk a-b-c-d or a-d-c-b,
you get the following summands:

    (12 - 1) + (3 - 10) + (8 - 5) + (9 - 4) = 11 - 7 + 3 + 5 = 12 = 2 * 6 
        a         b          c         d

Interestingly, in 2D this becomes extremely simple: On a polygon, we can simply use

    (x0 - border.left) * (y1 - y0) + (x0 - border.right) (y1 - y0)

because the orientation of the line segment will take care of the sign:

+ (y1 - y0) == 0: horizontal, no contribution
+ (y1 - y0) > 0: vertical downwards (in screen coordinates)
+ (y1 - y0) < 0: vertical upwards (in screen coordinates)

Similarly, (x - border.left) will always be non-negative while (x - border.right) will always be 
negative or zero.

_TODO:_ Check which is faster: filtering out horizontal edges before calculation or 
simply relying on `y1-y0 == 0`

## General

Polygons always define areas in clockwise direction. (Because of the inverted y coordinate,
this is mathematically counter-clockwise.)

