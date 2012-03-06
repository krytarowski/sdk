// Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

class _TextFactoryProvider {

  factory Text(data) => document._createTextNode(data);
}

class _EventFactoryProvider {
  factory Event(String type, [bool canBubble = true,
      bool cancelable = true]) {
    _EventImpl e = document._createEvent("Event");
    e._initEvent(type, canBubble, cancelable);
    return e;
  }
}

class _MouseEventFactoryProvider {
  factory MouseEvent(String type, Window view, int detail,
      int screenX, int screenY, int clientX, int clientY, int button,
      [bool canBubble = true, bool cancelable = true, bool ctrlKey = false,
      bool altKey = false, bool shiftKey = false, bool metaKey = false,
      EventTarget relatedTarget = null]) {
    final e = document._createEvent("MouseEvent");
    e._initMouseEvent(type, canBubble, cancelable, view, detail,
        screenX, screenY, clientX, clientY, ctrlKey, altKey, shiftKey, metaKey,
        button, relatedTarget);
    return e;
  }
}

class _CSSStyleDeclarationFactoryProvider {
  factory CSSStyleDeclaration.css(String css) {
    var style = new Element.tag('div').style;
    style.cssText = css;
    return style;
  } 

  factory CSSStyleDeclaration() {
    return new CSSStyleDeclaration.css('');
  }
}

final _START_TAG_REGEXP = const RegExp('<(\\w+)');
class _ElementFactoryProvider {
  static final _CUSTOM_PARENT_TAG_MAP = const {
    'body' : 'html',
    'head' : 'html',
    'caption' : 'table',
    'td': 'tr',
    'tbody': 'table',
    'colgroup': 'table',
    'col' : 'colgroup',
    'tr' : 'tbody',
    'tbody' : 'table',
    'tfoot' : 'table',
    'thead' : 'table',
    'track' : 'audio',
  };

  /** @domName Document.createElement */
  factory Element.html(String html) {
    // TODO(jacobr): this method can be made more robust and performant.
    // 1) Cache the dummy parent elements required to use innerHTML rather than
    //    creating them every call.
    // 2) Verify that the html does not contain leading or trailing text nodes.
    // 3) Verify that the html does not contain both <head> and <body> tags.
    // 4) Detatch the created element from its dummy parent.
    String parentTag = 'div';
    String tag;
    final match = _START_TAG_REGEXP.firstMatch(html);
    if (match !== null) {
      tag = match.group(1).toLowerCase();
      if (_CUSTOM_PARENT_TAG_MAP.containsKey(tag)) {
        parentTag = _CUSTOM_PARENT_TAG_MAP[tag];
      }
    }
    // TODO(jacobr): make type dom.HTMLElement when dartium allows it.
    _ElementImpl temp = document._createElement(parentTag);
    temp.innerHTML = html;

    Element element;
    if (temp.elements.length == 1) {
      element = temp.elements.first;
    } else if (parentTag == 'html' && temp.elements.length == 2) {
      // Work around for edge case in WebKit and possibly other browsers where
      // both body and head elements are created even though the inner html
      // only contains a head or body element.
      element = temp.elements[tag == 'head' ? 0 : 1];
    } else {
      throw new IllegalArgumentException('HTML had ${temp.elements.length} ' +
          'top level elements but 1 expected');
    }
    element.remove();
    return element;
  }

  /** @domName Document.createElement */
  factory Element.tag(String tag) {
    return document._createElement(tag);
  }
}