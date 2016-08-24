class Ribbon
{
  int ribbonAmount;
  float randomness;
  int ribbonParticleAmount;         // length of the Particle Array (max number of points)
  int particlesAssigned = 0;        // current amount of particles currently in the Particle array                                
  float radiusMax = 12;              // maximum width of ribbon
  float radiusDivide = 10;          // distance between current and next point / this = radius for first half of the ribbon
  float gravity = .03;              // gravity applied to each particle
  float friction = 1.1;             // friction applied to the gravity of each particle
  int maxDistance = 40;             // if the distance between particles is larger than this the drag comes into effect
  float drag = 2;                   // if distance goes above maxDistance - the points begin to grag. high numbers = less drag
  float dragFlare = .008;           // degree to which the drag makes the ribbon flare out
  RibbonParticle[] particles;       // particle array
  color ribbonColor;
  
  Ribbon(int ribbonParticleAmount, color ribbonColor, float randomness)
  {
    this.ribbonParticleAmount = ribbonParticleAmount;
    this.ribbonColor = ribbonColor;
    this.randomness = randomness;
    init();
  }
  
  void init()
  {
    particles = new RibbonParticle[ribbonParticleAmount];
  }
  
  void update(float randX, float randY)
  {
    addParticle(randX, randY);
    drawCurve();
  }
  
  void addParticle(float randX, float randY)
  {
    if(particlesAssigned == ribbonParticleAmount)
    {
      for (int i = 1; i < ribbonParticleAmount; i++)
      {
        particles[i-1] = particles[i];
      }
      particles[ribbonParticleAmount - 1] = new RibbonParticle(randomness, this);
      particles[ribbonParticleAmount - 1].px = randX;
      particles[ribbonParticleAmount - 1].py = randY;
      return;
    }
    else
    {
      particles[particlesAssigned] = new RibbonParticle(randomness, this);
      particles[particlesAssigned].px = randX;
      particles[particlesAssigned].py = randY;
      ++particlesAssigned;
    }
    if (particlesAssigned > ribbonParticleAmount) ++particlesAssigned;
  }
  
  void drawCurve()
  {
    smooth();
    for (int i = 1; i < particlesAssigned - 1; i++)
    {
      RibbonParticle p = particles[i];
      p.calculateParticles(particles[i-1], particles[i+1], ribbonParticleAmount, i);
    }

    fill(30);
    for (int i = particlesAssigned - 3; i > 1 - 1; i--)
    {
      RibbonParticle p = particles[i];
      RibbonParticle pm1 = particles[i-1];
      fill(ribbonColor, 255);
      if (i < particlesAssigned-3) 
      {
        noStroke();
        beginShape();
        vertex(p.lcx2, p.lcy2);
        bezierVertex(p.leftPX, p.leftPY, pm1.lcx2, pm1.lcy2, pm1.lcx2, pm1.lcy2);
        vertex(pm1.rcx2, pm1.rcy2);
        bezierVertex(p.rightPX, p.rightPY, p.rcx2, p.rcy2, p.rcx2, p.rcy2);
        vertex(p.lcx2, p.lcy2);
        endShape();
      }
    }
  }
}