/*

SimpleParticles.cpp

BlinkScript that allows to emit particles along a bezier curve
only one segment (start, end, start handle, end handle) of a curve possible at the moment

inputs: 
    format: sets the format
    noise: a 2d noise map
knobs:
    p1,p1h,p2, p2h -> bezier points and handles, hidden in gizmo
    start_frame, end_frame -> frame range
    curr_frame -> for BlinkScript use only, to get the time. A "frame" expression must be set for this to work. Will be hidden on th gizmo
    amount -> amount of particles emmited per frame
    lifetime -> lifetime of particles
    velocity, random_velocity -> velocity and random multiplier
    color -> color of the particles
    _mode -> 0 = cubicPoints, 1= circles
    pointSize -> only available when _mode is 1
    _max -> if true will merge particles per max, else plus


    random functions are derived from Erwan Leroy
    https://erwanleroy.com/making-3d-lightning-in-nuke-using-blinkscript/

    The cubicPlot is derived from Mads Hagbarth PointRender, with a cubic twist.
    https://higx.net/point_render/

    The circlePlot is derived from Nukes ParticleBlinkScriptRender Example
    
*/

// fract 
inline float fract(float x) {return x-floor(x);}

// random 
inline float random(float co) { return fract(sin(co*(91.3458f)) * 47453.5453f); }

// random 2d vector
inline float2 randomv(float2 seed)
{
  float scramble = random(seed.x + seed.y);
  float2 rand;
  rand.x = random(seed.x + scramble + 0.14557f + 0.47917f)*2-1;
  rand.y = random(seed.y * 0.214447f + scramble * 47.241f * seed.x)*2-1;
  return normalize(rand);
}

// get a point on the curve from t
inline float2 getBezierPoint(const float t, const float2 P0, const float2 P1, const float2 P2, const float2 P3){
    float2 ret;
    ret.x = pow(1.0f-t, 3) * P0.x + 3.0f * pow(1-t, 2) * t * P1.x + 3.0f * (1-t) * pow(t, 2) * P2.x + pow(t, 3) * P3.x;
    ret.y = pow(1.0f-t, 3) * P0.y + 3.0f * pow(1-t, 2) * t * P1.y + 3.0f * (1-t) * pow(t, 2) * P2.y + pow(t, 3) * P3.y;
    return ret;
}

// smoothstep for "cubic" filter
inline float smoothstep( float a, float b, float x ) {
    float t = clamp((x - a) / (b - a), 0.0, 1.0);
    return t*t * (3.0f - 2.0f*t);
  }
  

kernel SimpleParticles: ImageComputationKernel<ePixelWise>
{
    Image<eRead> format; // set format
    Image<eRead, eAccessRandom, eEdgeClamped> noise; // add noise
    Image<eWrite, eAccessRandom> dst;
    
    param:
        float2 p1;
        float2 p1h;
        float2 p2h;
        float2 p2;
        int start_frame;
        int end_frame;
        int curr_frame;
        int amount;
        int lifetime;
        float velocity;
        float random_velocity;
        float4 color;
        bool _mode;
        float pointSize;
        bool _max;

    local:
        int time;
        int max_amount;
        int _width;
        int _height;

    void define() {
        defineParam(p1, "point1", float2(10.0f, 10.0f));
        defineParam(p1h, "point1 handle", float2(20.0f, 10.0f));
        defineParam(p2h, "point2 handle", float2(30.0f, 10.0f));
        defineParam(p2, "point2", float2(40.0f, 10.0f));
        defineParam(start_frame, "start frame", 0);
        defineParam(end_frame, "end frame", 100);
        defineParam(curr_frame, "current frame", 0);
        defineParam(amount, "amount per frame", 20);
        defineParam(lifetime, "lifetime", 10);
        defineParam(velocity, "velocity", 1.0f);
        defineParam(random_velocity, "random velocity", 1.0f);
        defineParam(color, "color", float4(1.0f));
        defineParam(_mode, "mode", false);
        defineParam(pointSize, "Point Size", 1.5f);
        defineParam(_max, "max", false);
    }

    void init() {
        time = max(curr_frame-start_frame, 0);
        max_amount = (end_frame-start_frame) * amount;
        _width = format.bounds.width();
        _height = format.bounds.height();
    }

    //Write pixels to output.
    void draw(float posx,float posy,float weight=1.0f)
    { 
        float4 outcolor; //This is used to store the final output
        float4 inDst = (float4)dst(posx,posy); //Sample the destination image
        if (_max){
            // use max instead of plus
            outcolor = max(inDst, (color * weight));
        }
        else {
            // add pixels
            outcolor = inDst + (color * weight);
        }
        // write out 
        dst(posx,posy) = outcolor;
    }
  
    // Cubic filter
    void cubicPlot(float2 temppos)
    {
        float2 p;
        p.x=temppos.x - floor(temppos.x);
        p.y=temppos.y - floor(temppos.y);
        float weights[] = {(1.0f-p.x)*(1.0f-p.y), p.x*(1.0f-p.y), (1.0f-p.x)*p.y, p.x*p.y};
        int2 _position = int2(floor(temppos.x)-0,floor(temppos.y)-0); 
        draw(_position.x,_position.y,smoothstep(0.0f,1.0f,weights[0]));
        draw(_position.x+1,_position.y,smoothstep(0.0f,1.0f,weights[1]));
        draw(_position.x,_position.y+1,smoothstep(0.0f,1.0f,weights[2]));
        draw(_position.x+1,_position.y+1,smoothstep(0.0f,1.0f,weights[3]));
    }

    // draw circles
    void circlePlot( float2 xy)
    {
        float sizeSquared = pointSize * pointSize;
        float2 f = xy-floor(xy);
        float2 g = float2(1.0f) - f;
        xy = floor(xy);
        int size = ceil(pointSize);
        int minX = max(0, int(xy.x)-size);
        int maxX = min(_width-1, int(xy.x)+size);
        int minY = max(0, int(xy.y)-size);
        int maxY = min(_height-1, int(xy.y)+size);
        for ( int y = minY; y <= maxY; y++ ) {
        for ( int x = minX ; x <= maxX; x++ ) {
            float2 p = float2(x, y);
            float2 d = p-xy;
            float r2 = dot(d, d);
            if ( r2 < sizeSquared ) {
            float w = 1.0f-smoothstep(0, sizeSquared, r2);
            draw(p.x, p.y, w);
            }
        }
        }
    }
    
    void process(int2 pos) {
        if (pos.x || pos.y || time == 0 || curr_frame > end_frame + lifetime ) {
            return;
        }


        float age; //particle age
        float t; //t for bezier curve point
        float2 p_pos; // particle postion
        float2 direction; // random direction
        float4 sample_noise; // sample noise input

        float random_vel = clamp(random_velocity, 0.0f, 1.0f); // clamped random_velocity

        // loop though all particles
        for (int i=0; i< max_amount; i++) {
            float fi = float(i); // float index

            age = time -(fi / float(amount)); // age 
            if (age< 0 || age > lifetime) { // particle is not active anymore
                continue;
            }
            t = fi/float(max_amount-1.0f); // get t for bezier curve (0 = start point, 1= end point) 
            direction = randomv(float2 (i, i+250)) * age * velocity * (random(float(i+500)) * random_vel + (1.0f - random_vel));// random direction
            sample_noise = bilinear(noise, p_pos.x, p_pos.y)*(age/float(lifetime)); // noise sampled
            p_pos = getBezierPoint(t, p1, p1h, p2h, p2) + direction + float2(sample_noise.x, sample_noise.y); // position from bezier curve, direction and sampled noise
            if (format.bounds.inside(p_pos)) { // check if the pos values are within the format
                if (_mode) {
                    // draw cubic points
                    cubicPlot(p_pos);
                } else {
                    // draw circles
                    circlePlot(p_pos);
                }
            }

        }
    }

};