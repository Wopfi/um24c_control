## What's it for?

This little Python script was made to read data from a UM24C USB tester over
a Bluetooth connection.

## Serial Commands

| Hex Code | Function |
|----|--------------|
| f0 | Request Data |
| f1 | Next Page |
| f2 | Rotate Screen |
| f3 | Next Group |
| f4 | Reset Group Data |
| b0 - cd | Stop Current 0,0 - 0,29A |
| e0 - e9 | Screen off Timeout |
| d0 - d5 | Screen Brightness |
