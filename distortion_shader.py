from scene import *

distortion_shader = '''
precision highp float;
varying vec2 v_tex_coord;
// These uniforms are set automatically:
uniform sampler2D u_texture;
uniform float u_time;
uniform float u_r;
uniform float u_a;
uniform vec2 u_sprite_size;
// This uniform is set in response to touch events:
uniform vec2 u_offset;

void main(void) {
    vec2 p =  (v_tex_coord - u_offset)-0.5;
    float len = length(p)/u_r;
    vec2 uv = p*(1.0+(u_a-1.0)*exp(-len*len))+0.5+u_offset ;
    gl_FragColor = texture2D(u_texture,uv);
}
'''

class MyScene (Scene):
    def setup(self):
            self.sprite = SpriteNode('test:Ruler', size=(min(self.size),min(self.size)),parent=self)
            self.sprite.shader = Shader(distortion_shader)
            self.did_change_size()
            self.framecount=0
            self.Label= LabelNode(f'{self.framecount}',position=(100,100),size=(200,50),parent=self)
            self.bits= [SpriteNode(size=(32,32),position=(32,48*i+24),parent=self) for i in range(16)]

    def did_change_size(self):
            # Center the image:
            self.sprite.position = self.size - self.sprite.size/2
            self.sprite.shader.set_uniform('u_r',0.1)
            self.sprite.shader.set_uniform('u_a',2.0)

    def touch_began(self, touch):
            self.set_ripple_center(touch)

    def touch_moved(self, touch):
            self.set_ripple_center(touch)
    def update(self):
      for i,sn in enumerate(self.bits):
        sn.color=('black','white')[(self.framecount>>i)&1]
      
      self.Label.text=f'{self.framecount}'
      self.framecount+=1

    def set_ripple_center(self, touch):
            # Center the ripple effect on the touch location by setting the `u_offset` shader uniform:
            dx, dy = touch.location-self.sprite.position
            self.sprite.shader.set_uniform('u_offset', (dx/self.sprite.size.x, dy/self.sprite.size.y))
S=MyScene()
run(S,show_fps=True)
