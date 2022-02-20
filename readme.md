# Panorama JS Typings Generator

Simple python script that parses the output of the command `dump_panorama_js_scopes` from CS:GO, Dota 2, or Chaos Engine games and converts it to JSDoc for typing information of `$`, APIs, and panel types.

## Usage

```bash
python panorama_jsdoc_gen.py [dump_panorama_js_scopes_output] [outfile]
```

The outfile can then be placed inside of your game's `panorama/scripts/` folder.
VS Code's built-in typescript extension will recognize it (if its file extension is `.js`), giving you autocomplete, hover, and other features for `$` and your game's APIs.

Panels can also be given types via JSDoc for the same features: 
```javascript
/** @type {ProgressBar} @static */
progressBarPanel = $('#ProgressBarPanelID')
```

If VS Code or your text editor of choice fails to automatically import typing information, you can get them while developing via `require`, though the script will error with that in-game.

## Notes

Unfortunately we are unable to define Panorama's types via purely virtual JSDoc comments, so the output typings file contains dummy namespaces, classes, fields, and methods to fake typing information.

It is also impossible to have typing information for `$()`, considering `$` is itself a namespace with fields and methods.

## Other Panorama Development Resources

Check out the extension adding Panorama support for CSS/SCSS [here](https://marketplace.visualstudio.com/items?itemName=braemie.panorama-css).
