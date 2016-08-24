class RibbonParticle
{
  float px, py;                                       // x and y position of particle (this is the bexier point)
  float xSpeed, ySpeed = 0;                           // speed of the x and y positions
  float cx1, cy1, cx2, cy2;                           // the avarage x and y positions between px and py and the points of the surrounding Particles
  float leftPX, leftPY, rightPX, rightPY;             // the x and y points of that determine the thickness of this segment
  float lpx, lpy, rpx, rpy;                           // the x and y points of the outer bezier points
  float lcx1, lcy1, lcx2, lcy2;                       // the avarage x and y positions between leftPX and leftPX and the left points of the surrounding Particles
  float rcx1, rcy1, rcx2, rcy2;                       // the avarage x and y positions between rightPX and rightPX and the right points of the surrounding Particles
  float radius;                                       // thickness of current particle
  float randomness;
  Ribbon ribbon;
  
  RibbonParticle(float randomness, Ribbon ribbon)
  {
    this.randomness = randomness;
    this.ribbon = ribbon;
  }
  
  void calculateParticles(RibbonParticle pMinus1, RibbonParticle pPlus1, int particleMax, int i)
  {
    float div = 2;
    cx1 = (pMinus1.px + px) / div;
    cy1 = (pMinus1.py + py) / div;
    cx2 = (pPlus1.px + px) / div;
    cy2 = (pPlus1.py + py) / div;

    // calculate radians (direction of next point)
    float dx = cx2 - cx1;
    float dy = cy2 - cy1;

    float pRadians = atan2(dy, dx);

    float distance = sqrt(dx*dx + dy*dy);

    if (distance > ribbon.maxDistance)   //  && i > 1 
    {
      float oldX = px;
      float oldY = py;
      px = px + ((ribbon.maxDistance/ribbon.drag) * cos(pRadians));
      py = py + ((ribbon.maxDistance/ribbon.drag) * sin(pRadians));
      xSpeed += (px - oldX) * ribbon.dragFlare;
      ySpeed += (py - oldY) * ribbon.dragFlare;
    }
    
    ySpeed += ribbon.gravity;
    xSpeed *= ribbon.friction;
    ySpeed *= ribbon.friction;
    px += xSpeed + random(.3);
    py += ySpeed + random(.3);
    
    float randX = ((randomness / 2) - random(randomness)) * distance;
    float randY = ((randomness / 2) - random(randomness)) * distance;
    px += randX;
    py += randY;
    
    //float radius = distance / 2;
    //if (radius > radiusMax) radius = ribbon.radiusMax;
    
    if (i > particleMax / 2) 
    {
      radius = distance / ribbon.radiusDivide;
    } 
    else 
    {
      radius = pPlus1.radius * .9;
    }
    
    if (radius > ribbon.radiusMax) radius = ribbon.radiusMax;
    if (i == particleMax - 2 || i == 1) 
    {
      if (radius > 1) radius = 1;
    }

    // calculate the positions of the particles relating to thickness
    leftPX = px + cos(pRadians + (HALF_PI * 3)) * radius;
    leftPY = py + sin(pRadians + (HALF_PI * 3)) * radius;
    rightPX = px + cos(pRadians + HALF_PI) * radius;
    rightPY = py + sin(pRadians + HALF_PI) * radius;

    // left and right points of current particle
    lpx = (pMinus1.lpx + lpx) / div;
    lpy = (pMinus1.lpy + lpy) / div;
    rpx = (pPlus1.rpx + rpx) / div;
    rpy = (pPlus1.rpy + rpy) / div;

    // left and right points of previous particle
    lcx1 = (pMinus1.leftPX + leftPX) / div;
    lcy1 = (pMinus1.leftPY + leftPY) / div;
    rcx1 = (pMinus1.rightPX + rightPX) / div;
    rcy1 = (pMinus1.rightPY + rightPY) / div;

    // left and right points of next particle
    lcx2 = (pPlus1.leftPX + leftPX) / div;
    lcy2 = (pPlus1.leftPY + leftPY) / div;
    rcx2 = (pPlus1.rightPX + rightPX) / div;
    rcy2 = (pPlus1.rightPY + rightPY) / div;
  }
}
