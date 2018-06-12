# ProFits
ProFits is an [EVE Online](http://eveonline.com) hull fitting resource. 
The application intercepts killmails on their way to [zKillboard](https://zkillboard.com)
and performs some basic data analysis (e.g. what are the top ten
most common items fitted on a Catalyst), after which Flask is used
to allow users to view the information.

## Usage
Currently the application is in a standalone state to be run
on a local machine which can be viewed as a web page. The web page 
lists the ships it the application has information on complete with
hyperlinks allowing users to view more detailed information per ship.
Ideally this entire app would be running on its own machine with its own
cleanup routines but currently that is not the case.

## License
[This program is licensed under the "MIT License"]

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so,
subject to the following conditions:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
