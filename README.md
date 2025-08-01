<h1 align="center">Fothelia</h1>

<p align="center">
  <a href="https://github.com/4strium/Fothelia/releases"><img src="https://img.shields.io/github/release/4strium/Fothelia" alt="Latest Release"></a>
  <img src="https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows11&logoColor=white" alt="Windows Badge">
  <img src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black" alt="Linux Badge"><br/>
  <img src="https://raw.githubusercontent.com/4strium/Fothelia/refs/heads/main/images/splash.png" alt="Fothelia logo">
</p>

Fothelia is an ecosystem for controlling LED strip without any internet bridge, just by **Bluetooth** connection. 

<p>
  <img src="https://raw.githubusercontent.com/4strium/Fothelia/refs/heads/main/images/demoAnimation.gif"  width="100%" alt="Animated GIF demonstration">
</p>

You will need some parts and a you're going to need to do a bit of very simple tinkering to take control of the LED strip, but believe me, it will STILL cost you less than buying extension kits — when all you wanted was to use the leftover piece of strip that's been sitting in your closet...

## Building the controller device
By the end your controller device should be looking like this :

If you can print the enclosure with a 3D printer, the following CAD project files are available in the [`CAD`](https://github.com/4strium/Fothelia/tree/main/CAD) directory. The box can be big since the `Dollatek LR784 MOSFET Control Module` i am using are huge, thus it is mandatory to provide space inside. 

By the way, why using this type of MOSFET and not just cheap MOSFET ? The reason is simple : **Input voltage of LED strip**, on my side I am using a regular Philips HUE led strip but in fact this led strip work with an input voltage of **24V**, so we need a transistor capable to manage this amount of voltage (typically used in industry), and not the type of MOSFET used in low-voltage electronic circuit.

### Alimentation
Therefore, we will need to have a 24V alimentation in our circuit, on my side I choose to boost the 5V output of the ESP32 to obtain the desired 24V (but there is plenty of other solution to ensure that). I'm using a DC power step up called `MT3608`, and it is working fine, I don't have any issues with this solution!

### Control using PWM
The goal is now to control the different MOSFET with PWM of the board you're using. If you look closely to one of the two end of the ribbon, you will notice that we have six inputs :
* C -> Cold White LED's
* B -> Blue component of RGB LED's
* G -> Green component of RGB LED's
* R -> Red component of RGB LED's
* F -> Warm White LED's
* Vcc -> +24V power

<p align='center'>
  <img src="https://raw.githubusercontent.com/4strium/Fothelia/refs/heads/main/images/inputs.jpg" alt="LED strip inputs">
</p>