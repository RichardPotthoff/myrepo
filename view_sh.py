import ui
import sys
import io
import types

# Make sure to import your existing generator engine from your background file
from gen_sh import sh_engine, cloned_packages_path

class RobustUIStreamProxy:
    """
    An advanced stream proxy that passes an explicit color setting 
    down to the textview panel layer.
    """
    encoding = 'utf-8'
    errors = 'strict'
    _fileno = 1
    
    # 🔥 ADD: color parameter defaults to None (uses standard black text)
    def __init__(self, view_reference, name="stdout", fd=1, color=None):
        self.view = view_reference
        self.name = name
        self._fileno = fd
        self.color = color # Saves the text color mapping for this stream

    def write(self, s):
        if s and s.strip():
            # 🔥 CHANGE: Pass the stream's color attribute down to the logger!
            self.view.log_text(s.strip(), color=self.color)

    def flush(self):
        pass

    def fileno(self):
        return self._fileno

    @property
    def closed(self):
        return False
        
class CustomShellView(ui.View):
    def __init__(self, engine_generator):
        self.engine = engine_generator
        self.name = "My Algorithm Shell"
        self.background_color = '#ffffff'
        self.kb_frame = (0, 0, 0, 0)
        
        # 1. Output Screen Area
        self.output_area = ui.TextView()
        self.output_area.font = ('Menlo', 14)
        self.output_area.text_color = '#000000'
        self.output_area.background_color = '#ffffff'
        self.output_area.editable = False
        self.add_subview(self.output_area)
        
        # 2. Keyboard Input Box
        self.input_field = ui.TextField()
        self.input_field.font = ('Menlo', 14)
        self.input_field.background_color = '#ffffff'
        self.input_field.text_color = '#000000'
        self.input_field.border_color = '#cccccc'
        self.input_field.border_width = 1
        self.input_field.autocorrection_type = False
        self.input_field.autocapitalization_type = ui.AUTOCAPITALIZE_NONE
        self.input_field.action = self.on_enter_pressed 
        self.add_subview(self.input_field)
        

        # 3. Standard Output stays normal black text
        self.stdout_proxy = RobustUIStreamProxy(self, "stdout", 1, color=None)
        
        # 4. 🔥 ERROR OUTPUT IS CHOSEN AS CRISP RED TEXT!
        self.stderr_proxy = RobustUIStreamProxy(self, "stderr", 2, color='#c0392b')

        # Prime the shell engine loop
        self.current_prompt = next(self.engine)
        self.log_text(self.current_prompt)

    def keyboard_frame_will_change(self, frame):
        self.kb_frame = frame
        self.layout()
        ui.delay(self.scroll_to_bottom, 0.05)

    def layout(self):
        w, h = self.bounds.width, self.bounds.height
        kb_visible_height = 0
        if self.kb_frame and len(self.kb_frame) == 4:
            kb_y = self.kb_frame[1] # Use index 1 to find the absolute Y coordinate
            view_screen_origin = ui.convert_point((0, 0), from_view=self, to_view=None)
            view_screen_y = view_screen_origin[1]
            view_bottom_y = view_screen_y + h
            if kb_y > 0 and view_bottom_y > kb_y:
                kb_visible_height = view_bottom_y - kb_y

        input_height = 44
        margin = 10
        usable_height = h - kb_visible_height
        
        self.output_area.frame = (margin, margin, w - (margin * 2), usable_height - input_height - (margin * 3))
        self.input_field.frame = (margin, usable_height - input_height - margin, w - (margin * 2), input_height)

    def log_text(self, text, color=None):
        """Appends text to terminal history with matching font sizes and color support."""
        from objc_util import ObjCInstance, ObjCClass, UIColor
        
        # 1. Ensure we have a newline at the end
        string_to_append = str(text) + "\n"
        
        # 2. Get the low-level iOS TextView storage object
        tv_objc = ObjCInstance(self.output_area)
        text_storage = tv_objc.textStorage()
        
        # 3. Determine the color
        if color == '#c0392b':
            ios_color = UIColor.colorWithRed_green_blue_alpha_(192/255.0, 57/255.0, 43/255.0, 1.0)
        else:
            ios_color = UIColor.blackColor()
            
        # 4. 🔥 NEW: Fetch the native iOS Menlo font matching your 14pt input field size
        UIFont = ObjCClass('UIFont')
        ios_font = UIFont.fontWithName_size_('Menlo', 14.0)
        
        # 5. Look up the Objective-C layout classes dynamically
        NSDictionary = ObjCClass('NSDictionary')
        NSAttributedString = ObjCClass('NSAttributedString')
        
        # 🔥 UPDATED: Build the attributes dictionary containing BOTH color and font rules
        # Objective-C keys use specific strings: 'NSColor' and 'NSFont'
        keys = ['NSColor', 'NSFont']
        objects = [ios_color, ios_font]
        attributes = NSDictionary.dictionaryWithObjects_forKeys_(objects, keys)
        
        # 6. Create the iOS Attributed String pairing the text with our text style settings
        rich_text = NSAttributedString.alloc().initWithString_attributes_(string_to_append, attributes)
        
        # 7. Append it straight onto the screen storage window buffer!
        text_storage.appendAttributedString_(rich_text)
        rich_text.release()
            
        # Queue up the autoscroll routine safely
        ui.delay(self.scroll_to_bottom, 0.05)
        
    def scroll_to_bottom(self):
        """Forces the terminal text tracker to jump straight to the last line."""
        # 💡 FIX: Safely pull index 1 (Total Text Height) and index 3 (Window Box Height)
        total_text_height = self.output_area.content_size[1]
        window_box_height = self.output_area.bounds[3]
        
        # Calculate the size difference using flat scalar numbers
        size_difference = total_text_height - window_box_height
        
        if size_difference > 0:
            # Tell the content offset vector to scroll down exactly by that gap amount
            self.output_area.content_offset = (0, size_difference)

    def on_enter_pressed(self, sender):
        cmdln = sender.text
        sender.text = "" 
        self.log_text(f"> {cmdln}")
        
        # Cache original global execution environments safely
        old_stdout, old_stderr = sys.stdout, sys.stderr
        old_orig_stdout, old_orig_stderr = sys.__stdout__, sys.__stderr__
        
        # Force all system streams to read our proxy configurations
        sys.stdout, sys.__stdout__ = self.stdout_proxy, self.stdout_proxy
        sys.stderr, sys.__stderr__ = self.stderr_proxy, self.stderr_proxy
        
        try:
            # Step the execution engine forward using .send()
            self.current_prompt = self.engine.send(cmdln)
        except StopIteration:
            self.log_text("Shell process ended.")
            self.input_field.editable = False
        except Exception as gen_err:
            self.log_text(f"Execution Error: {gen_err}")
        finally:
            # Always cleanly restore state baselines to prevent IDE lockups
            sys.stdout, sys.stderr = old_stdout, old_stderr
            sys.__stdout__, sys.__stderr__ = old_orig_stdout, old_orig_stderr
            self.log_text(self.current_prompt)

# ==========================================
# 🔥 RESTORED MAIN EXECUTION BLOCK
# ==========================================
if __name__ == '__main__':
    # 1. Initialize the background engine generator thread
    engine_instance = sh_engine(cloned_packages_path)
    
    # 2. Build the visual terminal interface window
    view = CustomShellView(engine_instance)
    
    # 3. Dock it as an independent sliding panel layout inside Pythonista
    view.present('panel')
    
