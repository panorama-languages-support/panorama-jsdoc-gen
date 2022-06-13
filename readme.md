# Panorama JS Typings Generator

Simple python script that parses the output of the commands `dump_panorama_js_scopes` and `dump_panorama_events` from CS:GO, Dota 2, or Chaos Engine games and converts it to JSDoc for typing information of `$`, APIs, and panel types.

## Usage

```bash
python3 src/panorama_jsdoc_gen.py [js_scopes_outputfile] [js_events_outputfile] [outfile]
```

The outfile can then be placed inside of your game's `panorama/scripts/` folder.
VS Code's built-in typescript extension will recognize it and pull in the types only if you have it opened and its file extension is `.js`.
This will give you autocomplete, hover, and other features for `$` and your game's APIs. Event name autocompletion is included as well for `$.RegisterEventHandler` and `$.RegisterForUnhandledEvent`.

Panels can also be given types via JSDoc for the same features: 
```javascript
/** @type {ProgressBar} @static */
progressBarPanel = $('#ProgressBarPanelID')
```

If VS Code or your text editor of choice fails to automatically import typing information, you can get them while developing via `require`, though the script will error with that in-game.

## Supported Games

Currently only Momentum Mod and P2:CE types files are generated, but the converter should work for CS:GO and Dota 2.
Feel free to open an issue or pull request if you would like to see those games added here!

## Notes

Unfortunately we are unable to define Panorama's types via purely virtual JSDoc comments, so the output typings file contains dummy namespaces, classes, fields, and methods to fake typing information.

It is also impossible to have typing information for `$()`, considering `$` is itself a namespace with fields and methods. However, a snippet for that is available in [this vscode extension](https://marketplace.visualstudio.com/items?itemName=braemie.panorama-css).

## Other Panorama Development Resources

Check out the extension adding Panorama support for CSS/SCSS [here](https://marketplace.visualstudio.com/items?itemName=braemie.panorama-css).
