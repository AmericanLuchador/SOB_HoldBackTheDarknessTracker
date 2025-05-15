<body>
This project utilizes an ESP32S3 to control dice rolling and tracking for the Hold Back the Darkness feature in the Shadows of Brimstone board game.

In the winter quarter of 2025, I took a Principles of Computer Science class, which taught the basics of the Python programming language. To practice what I learned, I built a simple dice roller on my PC. I wanted it to be more purpose-built, so I expanded it to return specific results based on the Hold Back the Darkness feature of my favorite board game, Shadows of Brimestone. It was a simple build but I wanted something smaller and portable, which is where the ESP32S3 came in. Long story short, I wired up the ESP32S3 with some buttons, an LCD display, and a NeoPixel ring before rewriting the code to take advantage of these components.

Features:
<ul>
  <li>Press a button to roll the dice.</li>
  <li>The LCD display shows the result of each die and the total amount.</li>
  <li>When a double is rolled, the LCD display will show the results of the Depth Event Chart.</li>
    <ul>
      <li>Other Worlds have their own Depth Event Chart. When entering an Other World, cycle through to the right world by pressing the appropriate button.</li>
      <li>The current version only has a couple of Other Worlds, but more can easily be added.</li>
    </ul>
  <li>NeoPixel ring displays the current location of the players and the Darkness.</li>
    <ul>
      <li>The players move forward or backward with the press of the appropriate button.</li>
      <li>The Darkness moves automatically based on the results of the dice roll.</li>
      <li>The Darkness can be moved forward or backward with the press of the appropriate button.</li>
      <li>When the Darkness lands on a Growing Dread or Darkness marker, the LCD display and the NeoPixel will alert the player.</li>
    </ul>
  <li>Location markers are automatically saved. The device can be turned off and your locations will be restored when turned back on.</li>
    <ul>
      <li>Hold down a specific button for 10 seconds to reset the game.</li>
    </ul>
  <li>Should the Darkness escape, the NeoPixel will flash wildly for several seconds before resetting everything.</li>
</ul>



Additional information and details will be added.
</body>
