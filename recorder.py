import os
import json
import time
from pynput import mouse, keyboard

class Recorder:
    def __init__(self):
        self.action_list = []
        self.mouse_listener = None
        self.keyboard_listener = None
        self.listeners_active = False
        self.start_time = None
        # self.keys_pressed = []
        self.delete_last_actions = True

    def _log_action(self, action_type: str, details: json) -> None:
        """ Saves the a user input into the action_list.

        Args:
            action_type (str): e.g. mouse_scroll.
            details (json): Any additional information about the action, like location on screen.

        Returns:
            None
        """
        if self.listeners_active:
            timestamp = time.time() - self.start_time
            self.action_list.append({
                "timestamp": timestamp,
                "type": action_type,
                "details": details
            })

    def _init_recording(self) -> None:
        """ Initializes the recordings by setting self.start_time to now.

        Args:
            None

        Returns:
            None
        """
        self.start_time = time.time()

    def _start_mouse_listener(self) -> None:
        """ Defines the what should happen at different mouse events. Initializes and starts the listener.

        Args:
            None

        Returns:
            None
        """
        if not self.listeners_active:
            def on_click(x: int, y: int, button: object, pressed: bool) -> None:
                if pressed:
                    action_type = "mouse_button_down"
                    details = {
                        "location": {
                            "x": x, 
                            "y": y
                        },
                        "button": str(button)
                    }
                else:
                    action_type = "mouse_button_up"
                    details = {
                            "location": {
                            "x": x, 
                            "y": y
                        },
                        "button": str(button)
                    }
                self._log_action(action_type, details)

            def on_scroll(x: int, y: int, dx: int, dy: int) -> None:
                action_type = "mouse_scroll"
                details = {
                    "location": {
                            "x": x, 
                            "y": y
                    },
                    "scroll_delta": {
                        "dx": dx,
                        "dy": dy
                    }
                }
                self._log_action(action_type, details)
            
            # TODO
            # def on_move(x:int, y:int) -> None:
            #     action_type = "mouse_move"
            #     details = {
            #         "position": (x, y)
            #     }
            #     self.log_action(action_type, details)

            self.mouse_listener = mouse.Listener(
                on_click=on_click,
                on_scroll=on_scroll,
                # on_move=on_move
            )
            self.mouse_listener.start()

    def _start_keyboard_listener(self) -> None:
        """ Defines the what should happen at different keyboard events. Initializes and starts the listener.

        Args:
            None

        Returns:
            None
        """
        if not self.listeners_active:
            def on_press(key: object) -> None:
                try:
                    key_name = key.char if hasattr(key, 'char') else str(key)
                    # self.keys_pressed.append(key_name)
                    action_type = "key_press"
                    details = {
                        "key": key_name, 
                        # "current_combination": self.keys_pressed
                    }
                    self._log_action(action_type, details)
                except Exception as e:
                    print(f"Error capturing key press: {e}")

            def on_release(key: object) -> None:
                try:
                    key_name = key.char if hasattr(key, 'char') else str(key)
                    action_type = "key_release"
                    details = {
                        "key": key_name
                    }
                    self._log_action(action_type, details)
                    # self.keys_pressed.remove(key_name)
                except Exception as e:
                    print(f"Error capturing key release: {e}")

            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.keyboard_listener.start()
    
    def _delete_last_actions(self) -> None:
        """ Deletes the last actions from action_list, because it was pressed only to stop recording, not a valid user input.

        Args:
            None

        Returns:
            None
        """
        self.action_list = self.action_list[:-2 or None]

    def start_listeners(self) -> None:
        """ Start listening to user inputs. The recorded action saved into self.action_list.
        Args:
            None

        Returns:
            None
        """
        if not self.listeners_active:
            self._init_recording()
            self._start_mouse_listener()
            self._start_keyboard_listener()
            self.listeners_active = True

    def stop_listeners(self):
        """ Stop listening to user input.

        Args:
            None
        
        Returns:
            None
        """
        if self.listeners_active:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            self._delete_last_actions() if self.delete_last_actions else None
            self.listeners_active = False
    
    def save_to_file(self, path: str=None, filename: str="recording.json") -> None:
        """ Save action_list to a local json file.

        Args:
            filename (str, optional): Defaults to "recording.json".
            path (str): Path to save the file to. Defaults to "/".

        Returns:
            None
        """
        if not self.listeners_active:
            # Current script's directory if no path is provided
            if path is None:
                path = os.path.dirname(os.path.abspath(__file__))
            try:
                # Check if folder exists, create if not
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
            
                # Check folder permission
                if not os.access(path, os.W_OK):
                    raise PermissionError(f"Cannot write to directory: {path}")
                
                full_path = os.path.join(path, filename)
                with open(full_path, 'w') as f:
                    json.dump(self.action_list, f, indent=4)
            except PermissionError as e:
                print(f"Permission Error: {e}")
            except FileNotFoundError as e:
                print(f"Invalid path: {e}")
            except (IOError, OSError) as e:
                print(f"Failed to save file {filename}: {e}")
            except TypeError as e:
                print(f"Error during serialization of action_list to JSON: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    def get_action_list(self) -> list[dict]:
        """ Getting the action_list with method.

        Args:
            None

        Returns:
            list[dict]: Action list that was recorded. Same as self.action_list.
        """
        return self.action_list   

if __name__ == "__main__":
    # For test purposes
    recorder = Recorder()
    recorder.start_listeners()
    recorder.listeners_active = True
    print("Recording started... Press Ctrl+c to stop.")
    try:
        while recorder.listeners_active:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Recording stopped.")
        recorder.stop_listeners()
        recorder.save_to_file()
