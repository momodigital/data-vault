# Corrected version of prediktor.py
class Colors:
    def __init__(self):
        self.red = "#FF0000"
        self.green = "#00FF00"
        self.blue = "#0000FF"

    def get_color(self, color_name):
        if color_name == 'red':
            return self.red
        elif color_name == 'green':
            return self.green
        elif color_name == 'blue':
            return self.blue
        else:
            raise ValueError(f'Unknown color: {color_name}')  

    # Additional methods and functionality can go here
# Rest of your code
