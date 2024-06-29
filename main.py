from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Header, Footer
from textual.containers import Container
from textual.widget import Widget
from textual.geometry import Size
from textual.strip import Strip

from textual.events import Blur, Focus, Mount
from textual.binding import Binding, BindingType
from textual.message import Message
from textual.reactive import reactive, var
from textual import on

import numpy as np
#from rich.text import Text
from rich.segment import Segment
from rich.style import Style
from rich.color import Color

from typing import ClassVar
import random

class Image(Widget, can_focus=True):
  """Display Image with Pixels"""

  BINDINGS: ClassVar[list[BindingType]] = [
    Binding("left","cursor_left","cursor left",show=False),
    Binding("right","cursor_right","cursor right",show=False),
    Binding("up","cursor_up","cursor up",show=False),
    Binding("down","cursor_down","cursor down",show=False),
    Binding("q","cursor_set_color","set color",show=True),
    Binding("w","cursor_get_color","get color",show=True),
  ]

  DEFAULT_CSS = """
  Image {
    width: auto;
    height: auto;
    border: heavy white;
  }
  Image:focus {
    border: heavy red;
    /*background: blue;*/
  }
  """

  _cursor_inverse = reactive(False)
  _m="▄" # \u2580"
  color: tuple = (0,0,0)
  cursor_blink_duration = 0.2
  cursor_offset_x:int = 2
  cursor_offset_y:int = 1

  class GetColor(Message):
    """
    Message send when color is selected
    """

    def __init__(self, color: tuple) -> None:
      self.color = color
      super().__init__()

    # @property
    # def control(self) -> Image:
      # return self.image
  
  def __init__(self, 
    dx: int, 
    dy: int,
    *,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
    disabled: bool = False
    ):
    """
    Creates Image Widget
    """
    super().__init__(name = name, id = id, classes = classes, disabled = disabled)

    self.dx = dy
    self.dy = dy
    self.dy2 = dy//2
    self._init_image()
  
  #def on_mount(self) -> None:
    #self._init_image()
    # self.styles.border = ('heavy', 'white')
    # self.styles.width = "auto"
    # self.styles.height = "auto"

  def on_focus(self) -> None:
    pass
    # Activate Timer
    #self.set_timer(self.cursor_blink_duration,)
    # self.time.pause()
    # self.time.resume()

  def _on_mount(self, _:Mount) -> None:
    self._cursor_timer = self.set_interval(
      self.cursor_blink_duration,
      self._toggle_cursor,
      pause = not self.has_focus
    )

  def _on_blur(self, _:Blur) -> None:
    self._cursor_timer.pause()
    self.cursor_inverse = False;

  def _on_focus(self, _:Focus) -> None:
    self._cursor_timer.resume()
    self.cursor_inverse = False;
  
  def _toggle_cursor(self):
    self._cursor_inverse = not self._cursor_inverse
    #call for refreas
    
  def _init_image(self):
    self.image = np.zeros((self.dy,self.dx,3))
    for y in range(self.dy):
      for x in range(self.dx):
        self.image[y,x,:] = (random.randint(0,256), random.randint(0,256), random.randint(0,256))

  def get_content_width(self, container: Size, viewport: Size) -> int:
    return self.dx

  def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
    return self.dy2

  def action_cursor_right(self) -> None:
    self.cursor_offset_x += 1
    if self.cursor_offset_x >= self.dx:
      self.cursor_offset_x = self.dx-1

  def action_cursor_left(self) -> None:
    self.cursor_offset_x -= 1
    if self.cursor_offset_x < 0:
      self.cursor_offset_x = 0

  def action_cursor_down(self) -> None:
      self.cursor_offset_y += 1
      if self.cursor_offset_y >= self.dy:
        self.cursor_offset_y = self.dy-1
  
  def action_cursor_up(self) -> None:
    self.cursor_offset_y -= 1
    if self.cursor_offset_y < 0:
      self.cursor_offset_y = 0

  def action_cursor_get_color(self) -> None:
    r = self.image[self.cursor_offset_y,self.cursor_offset_x,0]
    g = self.image[self.cursor_offset_y,self.cursor_offset_x,1]
    b = self.image[self.cursor_offset_y,self.cursor_offset_x,2]
    self.color = (r,g,b)
    self.post_message(Image.GetColor(self.color))

  def action_cursor_set_color(self) -> None:
    (r,g,b) = self.color
    self.image[self.cursor_offset_y,self.cursor_offset_x,0] = r 
    self.image[self.cursor_offset_y,self.cursor_offset_x,1] = g
    self.image[self.cursor_offset_y,self.cursor_offset_x,2] = b
  
  def render_line(self, y: int) -> Strip:
    if y >= self.dy2:
      return Strip.blank(self.size.width)
    # if self.has_focus:
      # return Strip.blank(self.size.width)
    segments = [
      Segment(f"{self._m}",
        Style(
          color=Color.from_rgb(
            self.image[y*2+1,x,0],
            self.image[y*2+1,x,1],
            self.image[y*2+1,x,2]
          ),
          bgcolor=Color.from_rgb(
            self.image[y*2,x,0],
            self.image[y*2,x,1],
            self.image[y*2,x,2]
          )
        )
      )
      for x in range(self.dx)
    ]
    # Cursor
    if self.has_focus and y == self.cursor_offset_y // 2 and self._cursor_inverse:
      x = self.cursor_offset_x
      fgcolor = Color.from_rgb(
          self.image[y*2+1,x,0],
          self.image[y*2+1,x,1],
          self.image[y*2+1,x,2]
        )
      if y*2+1 == self.cursor_offset_y:
        # r = 0 if self.image[y*2+1,x,0] > 128 else 255
        # g = 0 if self.image[y*2+1,x,1] > 128 else 255
        # b = 0 if self.image[y*2+1,x,2] > 128 else 255
        (r,g,b) = (0,0,0) if self.image[y*2+1,x,0]**2 + self.image[y*2+1,x,1]**2 + self.image[y*2+1,x,2]**2 > 3*128**2 else (255,255,255)
        fgcolor = Color.from_rgb(
          r,g,b
        )  
      bgcolor = Color.from_rgb(
          self.image[y*2,x,0],
          self.image[y*2,x,1],
          self.image[y*2,x,2]
        )
      if y*2 == self.cursor_offset_y:
        # r = 0 if self.image[y*2,x,0] > 128 else 255
        # g = 0 if self.image[y*2,x,1] > 128 else 255
        # b = 0 if self.image[y*2,x,2] > 128 else 255
        (r,g,b) = (0,0,0) if self.image[y*2,x,0]**2 + self.image[y*2,x,1]**2 + self.image[y*2,x,2]**2 > 3*128**2 else (255,255,255)
        bgcolor = Color.from_rgb(
          r,g,b
        )  
      segments[x] = Segment(
        f"{self._m}",
        # f"+",
        Style(
          color=fgcolor,
          bgcolor=bgcolor
        )
      )
    return Strip(segments,self.dx)

class Palette(Image):
  def __init__(self, 
    *,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
    disabled: bool = False
    ):
    """
    Creates Palette Widget
    """
    super().__init__(8,2, name = name, id = id, classes = classes, disabled = disabled)
      
  def _init_image(self) -> None:
    self.dy = 2
    self.dx = 8
    self.dy2 = self.dy // 2
    self.image = np.zeros((self.dy,self.dx,3))
    self.image[0,0,:] = (36, 38, 54)
    self.image[0,1,:] = (93, 39, 93)
    self.image[0,2,:] = (177, 62, 73)
    self.image[0,3,:] = (239, 125, 87)
    self.image[0,4,:] = (255, 205, 117)
    self.image[0,5,:] = (167, 240, 112)
    self.image[0,6,:] = (56, 183, 100)
    self.image[0,7,:] = (37,113,121) # 257179m
    self.image[1,0,:] = (41,54,111) # 29366fm
    self.image[1,1,:] = (59,93,201) # 3b5dc9m
    self.image[1,2,:] = (65,166,246) # 41a6f6m
    self.image[1,3,:] = (115,239,247) # 73eff7m
    self.image[1,4,:] = (244,244,244) # f4f4f4m
    self.image[1,5,:] = (148,176,194) # 94b0c2m
    self.image[1,6,:] = (86,108,134) # 566c86m
    self.image[1,7,:] = (51,60,87) # 333c57m

  def action_cursor_set_color(self) -> None:
    return None  

class TermPixelArtApp(App):
  """A Textual app for ddrawing pixel art in terminal"""
  CSS = """
  #main-a {
    align: center middle;
    /*border: heavy;
    padding: 2 4;*/
  }
  /*
  Header {
    height: 3;
  }*/
  """

  TITLE = "TermPixelArt"
  
  def compose(self) -> ComposeResult:
    """Create child widggets"""
    self.image = Image(20,20)
    yield Header()
    yield Footer()
    #ScrolableContainer
    yield Container(
      Palette(),
      self.image,
      id = "main-a"
    )
    # yield Image()

  @on(Image.GetColor)
  def on_select_color(self, event: Image.GetColor) -> None:
    self.image.color = event.color

  def on_palette_get_color(self, message: Image.GetColor) -> None:
    self.image.color = message.color
    

def main():
  print("TermPixelArt")
  app = TermPixelArtApp()
  app.run()

if __name__ == "__main__":
  main()
