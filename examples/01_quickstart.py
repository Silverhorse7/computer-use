"""
Example 01: Quickstart Computer Use.

Demonstrates window navigation, native clicking, typing, and capturing.
"""

from computer_use import ComputerUseController

def main():
    cu = ComputerUseController()
    
    # 1. Capture current screen state
    print("[1] Capturing active screen...")
    cu.capture("output_screen.png")
    
    # 2. Maximize target window
    print("[2] Maximizing window...")
    cu.maximize()
    
    # 3. Navigate to a web application
    print("[3] Navigating to target site...")
    cu.navigate("https://news.ycombinator.com")
    
    # 4. Scroll down
    print("[4] Scrolling down...")
    cu.scroll(-600)
    
    # 5. Capture final state
    print("[5] Capturing result...")
    cu.capture("output_hn.png")
    print("Quickstart completed successfully!")

if __name__ == "__main__":
    main()
