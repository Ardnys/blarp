import moderngl
import numpy as np
from PIL import Image


class ModernGL:
    def __init__(self):
        """Safe moderngl resource manager."""
        # === Shader sources ===
        # Blur shader from: https://github.com/Experience-Monks/glsl-fast-gaussian-blur
        # Sharpen shader from: https://github.com/couleurs/glsl-sharpen
        # Though I modified the sharpening algorithm a bit
        self.vertex_shader = """
        #version 330
        in vec2 in_vert;
        out vec2 v_uv;
        void main() {
            v_uv = in_vert * 0.5 + 0.5;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """

        self.frag_blur = """
        #version 330
        uniform sampler2D image;
        uniform vec2 resolution;
        uniform vec2 direction;
        in vec2 v_uv;
        out vec4 fragColor;

        vec4 blur5(sampler2D image, vec2 uv, vec2 resolution, vec2 direction) {
          vec4 color = vec4(0.0);
          vec2 off1 = vec2(1.3333333333333333) * direction;
          color += texture(image, uv) * 0.29411764705882354;
          color += texture(image, uv + (off1 / resolution)) * 0.35294117647058826;
          color += texture(image, uv - (off1 / resolution)) * 0.35294117647058826;
          return color; 
        }

        void main() {
          fragColor = blur5(image, v_uv, resolution, direction);
        }
        """

        self.frag_sharpen = """
        #version 330
        uniform sampler2D tex;
        uniform vec2 renderSize;
        uniform float adjust;
        in vec2 v_uv;
        out vec4 fragColor;

        vec4 sharpen(sampler2D tex, vec2 coords, vec2 renderSize, float a) {
            float dx = 1.0 / renderSize.x;
            float dy = 1.0 / renderSize.y;

            vec4 center = texture(tex, coords);
            vec4 up     = texture(tex, coords + vec2(0.0, -1.0 * dy));
            vec4 down   = texture(tex, coords + vec2(0.0,  1.0 * dy));
            vec4 left   = texture(tex, coords + vec2(-1.0 * dx, 0.0));
            vec4 right  = texture(tex, coords + vec2( 1.0 * dx, 0.0));

            return (4.0 * a + 1.0) * center - a * (up + down + left + right);
        }

        void main() {
            fragColor = sharpen(tex, v_uv, renderSize, adjust);
        }
        """
        self.ctx = moderngl.create_standalone_context(require=330)
        self.prog_blur = self.ctx.program(
            vertex_shader=self.vertex_shader, fragment_shader=self.frag_blur
        )
        self.prog_sharp = self.ctx.program(
            vertex_shader=self.vertex_shader, fragment_shader=self.frag_sharpen
        )

        # Fullscreen quad
        self.quad_buffer = self.ctx.buffer(
            np.array(
                [
                    -1.0,
                    -1.0,
                    1.0,
                    -1.0,
                    -1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                dtype="f4",
            ).tobytes()
        )

        self.vao_blur = self.ctx.vertex_array(
            self.prog_blur, [(self.quad_buffer, "2f", "in_vert")]
        )
        self.vao_sharp = self.ctx.vertex_array(
            self.prog_sharp, [(self.quad_buffer, "2f", "in_vert")]
        )

    def __enter__(self):
        return self

    def __exit__(self):
        """Release all allocated resources"""
        self.quad_buffer.release()
        self.vao_blur.release()
        self.vao_sharp.release()
        self.prog_blur.release()
        self.prog_sharp.release()

    # just in case
    def release_all(self):
        """Release all allocated resources"""
        self.quad_buffer.release()
        self.vao_blur.release()
        self.vao_sharp.release()
        self.prog_blur.release()
        self.prog_sharp.release()


class Blarp:
    def __init__(self, mgl: ModernGL):
        self.mgl = mgl

    def __call__(self, img: Image, n: int):
        """PIL image.
        n is the blarp iterations.
        returns blarped buffer as ndarray"""
        width, height = img.size
        img_data = np.frombuffer(img.tobytes(), dtype=np.uint8)

        tex_a = self.mgl.ctx.texture((width, height), 3, img_data)
        tex_b = self.mgl.ctx.texture((width, height), 3)
        tex_a.filter = (moderngl.LINEAR, moderngl.LINEAR)
        tex_b.filter = (moderngl.LINEAR, moderngl.LINEAR)

        fbo_a = self.mgl.ctx.framebuffer(color_attachments=[tex_a])
        fbo_b = self.mgl.ctx.framebuffer(color_attachments=[tex_b])

        for i in range(n):
            if i % 2 == 0:
                # Blur pass
                fbo_b.use()
                tex_a.use(0)
                self.mgl.prog_blur["image"] = 0
                self.mgl.prog_blur["resolution"] = (width, height)
                self.mgl.prog_blur["direction"] = (
                    (1.0, 0.0) if i % 4 < 2 else (0.0, 1.0)
                )
                self.mgl.vao_blur.render(moderngl.TRIANGLE_STRIP)
            else:
                # Sharpen pass
                fbo_a.use()
                tex_b.use(0)
                self.mgl.prog_sharp["tex"] = 0
                self.mgl.prog_sharp["adjust"] = 0.55
                self.mgl.prog_sharp["renderSize"] = (width, height)
                self.mgl.vao_sharp.render(moderngl.TRIANGLE_STRIP)

        final_tex = tex_a if n % 2 == 1 else tex_b
        result = np.frombuffer(final_tex.read(), dtype=np.uint8).reshape(
            (height, width, 3)
        )

        # one learns cleaning up memory the hard way
        fbo_a.release()
        fbo_b.release()
        tex_a.release()
        tex_b.release()

        return result
