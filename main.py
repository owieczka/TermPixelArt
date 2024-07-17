from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Header, Footer
from textual.containers import Container, Horizontal
from textual.widget import Widget
from textual.geometry import Size
from textual.strip import Strip

from textual.events import Blur, Focus, Mount
from textual.binding import Binding, BindingType
from textual.message import Message
from textual.reactive import reactive, var
from textual import on

import numpy as np
import imageio
#from rich.text import Text
from rich.segment import Segment
from rich.style import Style
from rich.color import Color

import argparse

from typing import ClassVar
import random

class DisplayColor(Widget, can_focus=False):
  """Display Active Color"""

  DEFAULT_CSS = """
  DisplayColor {
    width: auto;
    height: auto;
    /*border: heavy white;*/
    border: none;
    margin: 1;
  }
  """

  _m="▄" # \u2580"
  color: tuple = reactive((0,0,0))
  
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

  def get_content_width(self, container: Size, viewport: Size) -> int:
    return self.dx

  def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
    return self.dy2
  # def watch_color(self, color: tuple) -> None:
    # self.styles.background = Color.from_rgb(*color)
    
  def render_line(self, y: int) -> Strip:
    if y >= self.dy2:
      return Strip.blank(self.size.width)
    # if self.has_focus:
      # return Strip.blank(self.size.width)
    color = Color.from_rgb(
      self.color[0],
      self.color[1],
      self.color[2]
      )
    segments = [
      # Segment(f"{self._m}",
      Segment(" ",
        Style(
          color=color,
          bgcolor=color
        )
      )
      for x in range(self.dx)
    ]
    return Strip(segments,self.dx)
    
class Image(Widget, can_focus=True):
  """Display Image with Pixels"""

  BINDINGS: ClassVar[list[BindingType]] = [
    Binding("left","cursor_left","cursor left",show=False),
    Binding("right","cursor_right","cursor right",show=False),
    Binding("up","cursor_up","cursor up",show=False),
    Binding("down","cursor_down","cursor down",show=False),
    Binding("q","cursor_set_color","set color",show=True),
    Binding("w","cursor_get_color","get color",show=True),
    Binding("ctrl+s","save_image","save image"),
    Binding("ctrl+o","load_image","load image")
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
  dx:int = 20
  dy:int = 20

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

    self.dx = dx
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
    self.image = np.zeros((self.dy,self.dx,3),np.uint8)
    for y in range(self.dy):
      for x in range(self.dx):
        # self.image[y,x,:] = (random.randint(0,256), random.randint(0,256), random.randint(0,256))
        self.image[y,x,:] = self.color

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

  def action_save_image(self) -> None:
    imageio.imwrite("out.png",self.image)

  def action_load_image(self) -> None:
    self.load_image("out.png")

  def load_image(self, filename: str) -> None:
    self.image = imageio.imread(filename)
    self.dx = self.image.shape[1]
    self.dy = self.image.shape[0]
    self.dy2 = self.dy // 2
    self.styles.width = self.dx
    self.styles.height = self.dy2
  
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
  DEFAULT_CSS = """
    Palette {
      margin: 1;
      border: none;
    }
    Palette:focus {
      /*margin: 0;*/
      border: none;
      /*background: red;*/
      /*offset: -1 -1;*/
    }
  """
  
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

  def action_save_image(self) -> None:
    return None

  def action_load_image(self) -> None:
    return None

class TermPixelArtApp(App):
  """A Textual app for ddrawing pixel art in terminal"""
  CSS = """
  #main-a {
    align: center middle;
    /*border: heavy;
    padding: 2 4;*/
  }
  Horizontal {
    keyline: heavy white;
    width: auto;
    height: auto;
  }
  Horizontal:focus-within {
    keyline: heavy red;
  }
  /*
  Header {
    height: 3;
  }*/
  """

  TITLE = "TermPixelArt"
  image_size = (20,20)

  def __init__(self, image_size: tuple[int] | None = None):
    if image_size:
      # print(image_size)
      self.image_size = image_size

    self.image = Image(*self.image_size)
    self.display_color = DisplayColor(2,2)
        
    super().__init__()
    
  def open_file(self, filename: str) -> None:
    self.image.load_image(filename)
  
  def compose(self) -> ComposeResult:
    """Create child widggets"""
    yield Header()
    yield Footer()
    #ScrolableContainer
    yield Container(
      Horizontal(
        self.display_color,
        Palette()
      )
      ,
      self.image,
      id = "main-a"
    )
    # yield Image()

  @on(Image.GetColor)
  def on_select_color(self, event: Image.GetColor) -> None:
    self.image.color = event.color
    self.display_color.color = event.color
    
  # def on_palette_get_color(self, message: Image.GetColor) -> None:
    # self.image.color = message.color
    # self.display_color.color = message.color

def main():
  print("TermPixelArt")
  parser = argparse.ArgumentParser(
    prog = "TermPixelArt",
    description = "Draw pixel art directly in terminal"
  )
  parser.add_argument(
    "--size",
    nargs=2,
    type=int,
    help="Size of created image. By default 20 by 20 pixels", 
    metavar =("dx","dy")
  )
  parser.add_argument(
    "-o",
    type=str,
    help="File name to open.",
    metavar = "filename"
  )
  args = parser.parse_args()
  image_size = args.size
  filename_open = args.o
  # print(args)
  # print(image_size)
  app = TermPixelArtApp(image_size)
  if filename_open:
    if image_size:
      print(f"Provided size will not affect canvas size")
    app.open_file(filename_open)
  app.run()

if __name__ == "__main__":
  main()
