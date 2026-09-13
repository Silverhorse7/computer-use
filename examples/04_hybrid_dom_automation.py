"""
Example 04: Hybrid DevTools DOM Injection (<20ms).

Demonstrates direct synthetic event dispatching for buttons, radio groups,
and text inputs on dynamic web applications.
"""

from computer_use import ComputerUseController

def main():
    cu = ComputerUseController()

    print("[1] Selecting deployment tier by semantic label...")
    cu.dom.select_radio("High Availability Multi-Region")

    print("[2] Filling cluster configuration parameter...")
    cu.dom.fill_input("Cluster Identifier", "prod-primary-01")

    print("[3] Clicking primary confirmation button...")
    cu.dom.click_button("Deploy Changes")

    print("DOM automation completed in milliseconds!")

if __name__ == "__main__":
    main()
