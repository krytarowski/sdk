#!/usr/bin/python
# Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
# for details. All rights reserved. Use of this source code is governed by a
# BSD-style license that can be found in the LICENSE file.

"""This module provides shared functionality for the system to generate
Dart:html APIs from the IDL database."""

from systemfrog import *
from systeminterface import *

# Members from the standard dom that should not be exposed publicly in dart:html
# but need to be exposed internally to implement dart:html on top of a standard
# browser.
_private_html_members = set([
  'Element.clientLeft',
  'Element.clientTop',
  'Element.clientWidth',
  'Element.clientHeight',
  'Element.offsetLeft',
  'Element.offsetTop',
  'Element.offsetWidth',
  'Element.offsetHeight',
  'Element.scrollLeft',
  'Element.scrollTop',
  'Element.scrollWidth',
  'Element.scrollHeight',
  'Element.childElementCount',
  'Element.firstElementChild',
  'Element.hasAttribute',
  'Element.getAttribute',
  'Element.removeAttribute',
  'Element.setAttribute',
  'Element.className',
  'Element.children',
  'Element.querySelectorAll',
  'Document.querySelectorAll',
  'Element.getBoundingClientRect',
  'Element.getClientRects',
  'Node.appendChild',
  'Node.removeChild',
  'Node.replaceChild',
  'Node.attributes',
  'Node.childNodes',
  'Document.createElement',
  'Document.createEvent',
  'Document.createTextNode',
  'Document.createTouchList',
  'Window.getComputedStyle',
  'EventTarget.removeEventListener',
  'EventTarget.addEventListener',
  'EventTarget.dispatchEvent',
  'Event.initEvent',
  'MouseEvent.initMouseEvent',
])

# Members from the standard dom that exist in the dart:html library with
# identical functionality but with cleaner names.
_html_library_renames = {
    'Document.defaultView': 'window',
    'DocumentFragment.querySelector': 'query',
    'Element.querySelector': 'query',
    'Element.webkitMatchesSelector' : 'matchesSelector',
    'Element.scrollIntoViewIfNeeded': 'scrollIntoView',
    'Document.querySelector': 'query',
    'DocumentFragment.querySelectorAll': 'queryAll',
    'DocumentFragment.querySelectorAll': 'queryAll',
    'Node.cloneNode': 'clone',
    'Node.nextSibling': 'nextNode',
    'Node.ownerDocument': 'document',
    'Node.parentNode': 'parent',
    'Node.previousSibling': 'previousNode',
    'Node.textContent': 'text',
}

#TODO(jacobr): inject annotations into the interfaces based on this table and
# on _html_library_renames.
_injected_doc_fragments = {
    'Element.query': '  /** @domName querySelector, Document.getElementById */',
}
# Members and classes from the dom that should be removed completelly from
# dart:html.  These could be expressed in the IDL instead but expressing this
# as a simple table instead is more concise.
# Syntax is: ClassName.(get\.|set\.)?MemberName
# Using get: and set: is optional and should only be used when a getter needs
# to be suppressed but not the setter, etc. 
# TODO(jacobr): cleanup and augment this list.
_html_library_remove = set([
    'Window.get:document', # Removed as we have a custom implementation.
    'NodeList.item',
    "Attr.*",
#    "BarProp.*",
#    "BarInfo.*",
#    "Blob.webkitSlice",
#    "CDATASection.*",
#    "Comment.*",
#    "DOMImplementation.*",
    # TODO(jacobr): listing title here is a temporary hack due to a frog bug
    # involving when an interface inherits from another interface and defines
    # the same field. BUG(1633)
    "Document.title",
    "Element.title",
    "Document.get:documentElement",
    "Document.get:forms",
#    "Document.get:selectedStylesheetSet",
#    "Document.set:selectedStylesheetSet",
#    "Document.get:preferredStylesheetSet",
    "Document.get:links",
    "Document.getElementsByTagName",
    "Document.set:domain",
    "Document.get:implementation",
    "Document.createAttributeNS",
    "Document.get:inputEncoding",
    "Document.getElementById",
    "Document.getElementsByClassName",
    "Element.getElementsByClassName",
    "Element.getElementsByTagNameNS",
    "Element.getElementsByTagName",
    "Document.get:compatMode",
    "Document.importNode",
    "Document.evaluate",
    "Document.get:images",
    "Document.querySelector",
    "Document.createExpression",
    "Document.getOverrideStyle",
    "Document.xmlStandalone",
    "Document.createComment",
    "Document.adoptNode",
    "Document.get:characterSet",
    "Document.createAttribute",
    "Document.querySelectorAll",
    "Document.get:URL",
    "Document.createElementNS",
    "Document.createEntityReference",
    "Document.get:documentURI",
    "Document.set:documentURI",
    "Document.createNodeIterator",
    "Document.createProcessingInstruction",
    "Document.get:doctype",
    "Document.getElementsByName",
    "Document.createTreeWalker",
    "Document.location",
    "Document.createNSResolver",
    "Document.get:xmlEncoding",
    "Document.get:defaultCharset",
    "Document.get:applets",
    "Document.getSelection",
    "Document.xmlVersion",
    "Document.get:anchors",
    "Document.getElementsByTagNameNS",
    "DocumentType.*",
    "Element.hasAttributeNS",
    "Element.getAttributeNS",
    "Element.setAttributeNode",
    "Element.getAttributeNode",
    "Element.removeAttributeNode",
    "Element.removeAttributeNS",
    "Element.setAttributeNodeNS",
    "Element.getAttributeNodeNS",
    "Element.setAttributeNS",
    "BodyElement.text",
    "AnchorElement.text",
    "OptionElement.text",
    "ScriptElement.text",
    "TitleElement.text",
#    "EventSource.get:url",
# TODO(jacobr): should these be removed?
    "Document.close",
    "Document.hasFocus",

    "Document.vlinkColor",
    "Document.captureEvents",
    "Document.releaseEvents",
    "Document.get:compatMode",
    "Document.designMode",
    "Document.dir",
    "Document.all",
    "Document.write",
    "Document.fgColor",
    "Document.bgColor",
    "Document.get:plugins",
    "Document.alinkColor",
    "Document.get:embeds",
    "Document.open",
    "Document.clear",
    "Document.get:scripts",
    "Document.writeln",
    "Document.linkColor",
    "Element.get:itemRef",
    "Element.outerText",
    "Element.accessKey",
    "Element.get:itemType",
    "Element.innerText",
    "Element.set:outerHTML",
    "Element.itemScope",
    "Element.itemValue",
    "Element.itemId",
    "Element.get:itemProp",
    'Element.scrollIntoView',
    "EmbedElement.getSVGDocument",
    "FormElement.get:elements",
    "HTMLFrameElement.*",
    "HTMLFrameSetElement.*",
    "HTMLHtmlElement.version",
#    "IFrameElement.getSVGDocument",  #TODO(jacobr): should this be removed
    "InputElement.dirName",
    "HTMLIsIndexElement.*",
    "ObjectElement.getSVGDocument",
    "HTMLOptionsCollection.*",
    "HTMLPropertiesCollection.*",
    "SelectElement.remove",
    "TextAreaElement.dirName",
    "NamedNodeMap.*",
    "Node.isEqualNode",
    "Node.get:TEXT_NODE",
    "Node.hasAttributes",
    "Node.get:DOCUMENT_TYPE_NODE",
    "Node.get:DOCUMENT_POSITION_FOLLOWING",
    "Node.lookupNamespaceURI",
    "Node.get:ELEMENT_NODE",
    "Node.get:namespaceURI",
    "Node.get:DOCUMENT_FRAGMENT_NODE",
    "Node.get:localName",
    "Node.dispatchEvent",
    "Node.isDefaultNamespace",
    "Node.compareDocumentPosition",
    "Node.get:baseURI",
    "Node.isSameNode",
    "Node.get:DOCUMENT_POSITION_DISCONNECTED",
    "Node.get:DOCUMENT_NODE",
    "Node.get:DOCUMENT_POSITION_CONTAINS",
    "Node.get:COMMENT_NODE",
    "Node.get:ENTITY_REFERENCE_NODE",
    "Node.isSupported",
    "Node.get:firstChild",
    "Node.get:DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC",
    "Node.get:lastChild",
    "Node.get:NOTATION_NODE",
    "Node.normalize",
    "Node.get:parentElement",
    "Node.get:ATTRIBUTE_NODE",
    "Node.get:ENTITY_NODE",
    "Node.get:DOCUMENT_POSITION_CONTAINED_BY",
    "Node.get:prefix",
    "Node.set:prefix",
    "Node.get:DOCUMENT_POSITION_PRECEDING",
    "Node.get:nodeType",
    "Node.removeEventListener",
    "Node.get:nodeValue",
    "Node.set:nodeValue",
    "Node.get:CDATA_SECTION_NODE",
    "Node.get:nodeName",
    "Node.addEventListener",
    "Node.lookupPrefix",
    "Node.get:PROCESSING_INSTRUCTION_NODE",
    "Notification.dispatchEvent",
    "Notification.addEventListener",
    "Notification.removeEventListener"])

# Events without onEventName attributes in the  IDL we want to support.
# We can automatically extract most event event names by checking for
# onEventName methods in the IDL but some events aren't listed so we need
# to manually add them here so that they are easy for users to find.
_html_manual_events = {
  'Element': ['touchleave', 'webkitTransitionEnd'],
  'Window': ['DOMContentLoaded']
}

# These event names must be camel case when attaching event listeners
# using addEventListener even though the onEventName properties in the DOM for
# them are not camel case.
_on_attribute_to_event_name_mapping = {
  'webkitanimationend': 'webkitAnimationEnd',
  'webkitanimationiteration': 'webkitAnimationIteration',
  'webkitanimationstart': 'webkitAnimationStart',
  'webkitspeechchange': 'webkitSpeechChange',
  'webkittransitionend': 'webkitTransitionEnd',
}

# Mapping from raw event names to the pretty camelCase event names exposed as
# properties in dart:html.  If the DOM exposes a new event name, you will need
# to add the lower case to camel case conversion for that event name here.
_html_event_names = {
  'DOMContentLoaded': 'contentLoaded',
  'touchleave': 'touchLeave',
  'abort': 'abort',
  'beforecopy': 'beforeCopy',
  'beforecut': 'beforeCut',
  'beforepaste': 'beforePaste',
  'beforeunload': 'beforeUnload',
  'blur': 'blur',
  'cached': 'cached',
  'canplay': 'canPlay',
  'canplaythrough': 'canPlayThrough',
  'change': 'change',
  'checking': 'checking',
  'click': 'click',
  'close': 'close',
  'contextmenu': 'contextMenu',
  'copy': 'copy',
  'cut': 'cut',
  'dblclick': 'doubleClick',
  'devicemotion': 'deviceMotion',
  'deviceorientation': 'deviceOrientation',
  'display': 'display',
  'downloading': 'downloading',
  'drag': 'drag',
  'dragend': 'dragEnd',
  'dragenter': 'dragEnter',
  'dragleave': 'dragLeave',
  'dragover': 'dragOver',
  'dragstart': 'dragStart',
  'drop': 'drop',
  'durationchange': 'durationChange',
  'emptied': 'emptied',
  'ended': 'ended',
  'error': 'error',
  'focus': 'focus',
  'hashchange': 'hashChange',
  'input': 'input',
  'invalid': 'invalid',
  'keydown': 'keyDown',
  'keypress': 'keyPress',
  'keyup': 'keyUp',
  'load': 'load',
  'loadeddata': 'loadedData',
  'loadedmetadata': 'loadedMetadata',
  'loadend': 'loadEnd',
  'loadstart': 'loadStart',
  'message': 'message',
  'mousedown': 'mouseDown',
  'mousemove': 'mouseMove',
  'mouseout': 'mouseOut',
  'mouseover': 'mouseOver',
  'mouseup': 'mouseUp',
  'mousewheel': 'mouseWheel',
  'noupdate': 'noUpdate',
  'obsolete': 'obsolete',
  'offline': 'offline',
  'online': 'online',
  'open': 'open',
  'pagehide': 'pageHide',
  'pageshow': 'pageShow',
  'paste': 'paste',
  'pause': 'pause',
  'play': 'play',
  'playing': 'playing',
  'popstate': 'popState',
  'progress': 'progress',
  'ratechange': 'rateChange',
  'readystatechange': 'readyStateChange',
  'reset': 'reset',
  'resize': 'resize',
  'scroll': 'scroll',
  'search': 'search',
  'seeked': 'seeked',
  'seeking': 'seeking',
  'select': 'select',
  'selectionchange': 'selectionChange',
  'selectstart': 'selectStart',
  'show': 'show',
  'stalled': 'stalled',
  'storage': 'storage',
  'submit': 'submit',
  'suspend': 'suspend',
  'timeupdate': 'timeUpdate',
  'touchcancel': 'touchCancel',
  'touchend': 'touchEnd',
  'touchmove': 'touchMove',
  'touchstart': 'touchStart',
  'unload': 'unload',
  'updateready': 'updateReady',
  'volumechange': 'volumeChange',
  'waiting': 'waiting',
  'webkitAnimationEnd': 'animationEnd',
  'webkitAnimationIteration': 'animationIteration',
  'webkitAnimationStart': 'animationStart',
  'webkitfullscreenchange': 'fullscreenChange',
  'webkitfullscreenerror': 'fullscreenError',
  'webkitSpeechChange': 'speechChange',
  'webkitTransitionEnd': 'transitionEnd'
}

def _OnAttributeToEventName(on_method):
  event_name = on_method.id[2:]
  if event_name in _on_attribute_to_event_name_mapping:
    return _on_attribute_to_event_name_mapping[event_name]
  else:
    return event_name

def _DomToHtmlEvents(interface_id, events):
  event_names = set(map(_OnAttributeToEventName, events)) 
  if interface_id in _html_manual_events:
    for manual_event_name in _html_manual_events[interface_id]:
      event_names.add(manual_event_name)

  return sorted(event_names, key=lambda name: _html_event_names[name])

# ------------------------------------------------------------------------------
class HtmlSystemShared(object):

  def __init__(self, database, generator):
    self._event_classes = set()
    self._seen_event_names = {}
    self._database = database
    self._generator = generator

  def _AllowInHtmlLibrary(self, interface, member, member_prefix):
    return not self._Matches(interface, member, member_prefix,
        _html_library_remove)

  def _Matches(self, interface, member, member_prefix, candidates):
    for interface_name in ([interface.id] +
        self._generator._AllImplementedInterfaces(interface)):
      if (DartType(interface_name) + '.' + member in candidates or
          DartType(interface_name) + '.' + member_prefix + member in candidates):
        return True
    return False

  def MaybeReturnDocument(self, return_type):
    """
    To make it appear that there are not a distinct Document and
    HTMLHtmlElement (document.documentElement) objects we always use
    documentElement instead of the regular document object so must not
    allow a regular document to leak out.
    """
    # TODO(jacobr): any method that returns a Node could also theoretically
    # really return a Document but there are alot of methods that return nodes
    # and they all appear to be safe.  Consider the alternate strategy of
    # whitelisting just the known safe methods that return Nodes.
    return (DartType(return_type) == 'EventTarget' or
        DartType(return_type) == 'Document')

  def RenameInHtmlLibrary(self, interface, member, member_prefix=''):
    """
    Returns the name of the member in the HTML library or None if the member is
    suppressed in the HTML library
    """
    if not self._AllowInHtmlLibrary(interface, member, member_prefix):
      return None

    for interface_name in ([interface.id] +
        self._generator._AllImplementedInterfaces(interface)):
      name = interface.id + '.' + member
      if name in _html_library_renames:
        return _html_library_renames[name]
      name = interface.id + '.' + member_prefix + member
      if name in _html_library_renames:
        return _html_library_renames[name]

    if self._PrivateInHtmlLibrary(interface, member, member_prefix):
      return '_' + member

    # No rename required
    return member

  def _PrivateInHtmlLibrary(self, interface, member, member_prefix):
    return self._Matches(interface, member, member_prefix,
        _private_html_members)

  # TODO(jacobr): this already exists
  def _TraverseParents(self, interface, callback):
    for parent in interface.parents:
      parent_id = parent.type.id
      if self._database.HasInterface(parent_id):
        parent_interface = self._database.GetInterface(parent_id)
        callback(parent_interface)
        self._TraverseParents(parent_interface, callback)

  # TODO(jacobr): this isn't quite right.... 
  def GetParentsEventsClasses(self, interface):
    # Ugly hack as we don't specify that Document inherits from Element
    # in our IDL.
    if interface.id == 'Document':
      return ['ElementEvents']

    interfaces_with_events = set()
    def visit(parent):
      if parent.id in self._event_classes:
        interfaces_with_events.add(parent)

    self._TraverseParents(interface, visit)
    if len(interfaces_with_events) == 0:
      return ['Events']
    else:
      names = []
      for interface in interfaces_with_events:
        names.append(interface.id + 'Events')
      return names

  def _ImplClassName(self, type_name):
    return '_' + type_name + 'Impl'

class HtmlSystem(System):

  def __init__(self, templates, database, emitters, output_dir, generator):
    super(HtmlSystem, self).__init__(
        templates, database, emitters, output_dir)
    self._shared = HtmlSystemShared(database, generator)

class HtmlInterfacesSystem(HtmlSystem):

  def __init__(self, templates, database, emitters, output_dir, generator):
    super(HtmlInterfacesSystem, self).__init__(
        templates, database, emitters, output_dir, generator)
    self._dart_interface_file_paths = []

  def InterfaceGenerator(self,
                         interface,
                         common_prefix,
                         super_interface_name,
                         source_filter):
    """."""
    interface_name = interface.id
    dart_interface_file_path = self._FilePathForDartInterface(interface_name)

    self._dart_interface_file_paths.append(dart_interface_file_path)

    dart_interface_code = self._emitters.FileEmitter(dart_interface_file_path)

    template_file = 'interface_%s.darttemplate' % interface_name
    template = self._templates.TryLoad(template_file)
    if not template:
      template = self._templates.Load('interface.darttemplate')

    return HtmlDartInterfaceGenerator(
        interface, dart_interface_code,
        template,
        common_prefix, super_interface_name,
        source_filter, self, self._shared)

  def ProcessCallback(self, interface, info):
    """Generates a typedef for the callback interface."""
    interface_name = interface.id
    file_path = self._FilePathForDartInterface(interface_name)
    self._ProcessCallback(interface, info, file_path)

  def GenerateLibraries(self, lib_dir):
    pass


  def _FilePathForDartInterface(self, interface_name):
    """Returns the file path of the Dart interface definition."""
    # TODO(jmesserly): is this the right path
    return os.path.join(self._output_dir, 'html', 'interface',
                        '%s.dart' % interface_name)

# ------------------------------------------------------------------------------

# TODO(jmesserly): inheritance is probably not the right way to factor this long
# term, but it makes merging better for now.
class HtmlDartInterfaceGenerator(DartInterfaceGenerator):
  """Generates Dart Interface definition for one DOM IDL interface."""

  def __init__(self, interface, emitter, template,
               common_prefix, super_interface, source_filter, system, shared):
    super(HtmlDartInterfaceGenerator, self).__init__(interface,
      emitter, template, common_prefix, super_interface, source_filter)
    self._system = system
    self._shared = shared

  def StartInterface(self):
    typename = self._interface.id

    extends = []
    suppressed_extends = []

    for parent in self._interface.parents:
      # TODO(vsm): Remove source_filter.
      if MatchSourceFilter(self._source_filter, parent):
        # Parent is a DOM type.
        extends.append(DartType(parent.type.id))
      elif '<' in parent.type.id:
        # Parent is a Dart collection type.
        # TODO(vsm): Make this check more robust.
        extends.append(DartType(parent.type.id))
      else:
        suppressed_extends.append('%s.%s' %
            (self._common_prefix, DartType(parent.type.id)))

    comment = ' extends'
    extends_str = ''
    if extends:
      extends_str += ' extends ' + ', '.join(extends)
      comment = ','
    if suppressed_extends:
      extends_str += ' /*%s %s */' % (comment, ', '.join(suppressed_extends))

    if typename in interface_factories:
      extends_str += ' default ' + interface_factories[typename]

    # TODO(vsm): Add appropriate package / namespace syntax.
    (self._members_emitter,
     self._top_level_emitter) = self._emitter.Emit(
         self._template + '$!TOP_LEVEL',
         ID=typename,
         EXTENDS=extends_str)

    element_type = MaybeTypedArrayElementType(self._interface)
    if element_type:
      self._members_emitter.Emit(
          '\n'
          '  $CTOR(int length);\n'
          '\n'
          '  $CTOR.fromList(List<$TYPE> list);\n'
          '\n'
          '  $CTOR.fromBuffer(ArrayBuffer buffer);\n',
        CTOR=self._interface.id,
        TYPE=DartType(element_type))

  def AddAttribute(self, getter, setter):
    html_getter_name = self._shared.RenameInHtmlLibrary(
      self._interface, getter.id, 'get:')
    html_setter_name = self._shared.RenameInHtmlLibrary(
      self._interface, getter.id, 'set:')

    if not html_getter_name:
      getter = None
    if not html_setter_name:
      setter = None
    if not getter and not setter:
      return

    # We don't yet handle inconsistent renames of the getter and setter yet.
    if html_getter_name and html_setter_name:
      assert html_getter_name == html_setter_name
    if (getter and setter and
        DartType(getter.type.id) == DartType(setter.type.id)):
      self._members_emitter.Emit('\n  $TYPE $NAME;\n',
                                 NAME=html_getter_name,
                                 TYPE=DartType(getter.type.id));
      return
    if getter and not setter:
      self._members_emitter.Emit('\n  final $TYPE $NAME;\n',
                                 NAME=html_getter_name,
                                 TYPE=DartType(getter.type.id));
      return
    raise Exception('Unexpected getter/setter combination %s %s' %
                    (getter, setter))

  def AddOperation(self, info):
    """
    Arguments:
      operations - contains the overloads, one or more operations with the same
        name.
    """
    html_name = self._shared.RenameInHtmlLibrary(self._interface, info.name)
    if html_name:
      self._members_emitter.Emit('\n'
                                 '  $TYPE $NAME($PARAMS);\n',
                                 TYPE=info.type_name,         
                                 NAME=html_name,
                                 PARAMS=info.ParametersInterfaceDeclaration())

  def FinishInterface(self):
    pass

  def AddConstant(self, constant):
    self._EmitConstant(self._members_emitter, constant)

  def AddEventAttributes(self, event_attrs):
    event_attrs = _DomToHtmlEvents(self._interface.id, event_attrs)
    self._shared._event_classes.add(self._interface.id)
    events_interface = self._interface.id + 'Events'
    self._members_emitter.Emit('\n  $TYPE get on();\n',
                               TYPE=events_interface)
    events_members = self._emitter.Emit(
        '\ninterface $INTERFACE extends $PARENTS {\n$!MEMBERS}\n',
        INTERFACE=events_interface,
        PARENTS=', '.join(
            self._shared.GetParentsEventsClasses(self._interface)))

    for event_name in event_attrs:
      if event_name in _html_event_names:
        events_members.Emit('\n  EventListenerList get $NAME();\n',
          NAME=_html_event_names[event_name])
      else:
        raise Exception('No known html even name for event: ' + event_name)

# ------------------------------------------------------------------------------

# TODO(jmesserly): inheritance is probably not the right way to factor this long
# term, but it makes merging better for now.
class HtmlFrogClassGenerator(FrogInterfaceGenerator):
  """Generates a Frog class for the dart:html library from a DOM IDL
  interface.
  """

  def __init__(self, system, interface, template, super_interface, dart_code,
      shared):
    super(HtmlFrogClassGenerator, self).__init__(
        system, interface, template, super_interface, dart_code)
    self._shared = shared

  def _ImplClassName(self, type_name):
    return self._shared._ImplClassName(type_name)

  def StartInterface(self):
    interface = self._interface
    interface_name = interface.id

    self._class_name = self._ImplClassName(interface_name)

    base = None
    if interface.parents:
      supertype = interface.parents[0].type.id
      if IsDartCollectionType(supertype):
        # List methods are injected in AddIndexer.
        pass
      else:
        base = self._ImplClassName(supertype)

    native_spec = MakeNativeSpec(interface.javascript_binding_name)

    extends = ' extends ' + base if base else ''

    # TODO: Include all implemented interfaces, including other Lists.
    implements = [interface_name]
    element_type = MaybeTypedArrayElementType(self._interface)
    if element_type:
      implements.append('List<%s>' % DartType(element_type))

    self._members_emitter = self._dart_code.Emit(
        self._template,
        #class $CLASSNAME$EXTENDS$IMPLEMENTS$NATIVESPEC {
        #$!MEMBERS
        #}
        CLASSNAME=self._class_name,
        EXTENDS=extends,
        IMPLEMENTS=' implements ' + ', '.join(implements),
        NATIVESPEC=' native "' + native_spec + '"')

    if element_type:
      self.AddTypedArrayConstructors(element_type)

  def AddIndexer(self, element_type):
    """Adds all the methods required to complete implementation of List."""
    # We would like to simply inherit the implementation of everything except
    # get length(), [], and maybe []=.  It is possible to extend from a base
    # array implementation class only when there is no other implementation
    # inheritance.  There might be no implementation inheritance other than
    # DOMBaseWrapper for many classes, but there might be some where the
    # array-ness is introduced by a non-root interface:
    #
    #   interface Y extends X, List<T> ...
    #
    # In the non-root case we have to choose between:
    #
    #   class YImpl extends XImpl { add List<T> methods; }
    #
    # and
    #
    #   class YImpl extends ListBase<T> { copies of transitive XImpl methods; }
    #
    self._members_emitter.Emit(
        '\n'
        '  $TYPE operator[](int index) native "return this[index];";\n',
        TYPE=self._NarrowOutputType(element_type))

    if 'CustomIndexedSetter' in self._interface.ext_attrs:
      self._members_emitter.Emit(
          '\n'
          '  void operator[]=(int index, $TYPE value) native "this[index] = value";\n',
          TYPE=self._NarrowInputType(element_type))
    else:
      # The HTML library implementation of NodeList has a custom indexed setter
      # implementation that uses the parent node the NodeList is associated
      # with if one is available.
      if self._interface.id != 'NodeList':
        self._members_emitter.Emit(
            '\n'
            '  void operator[]=(int index, $TYPE value) {\n'
            '    throw new UnsupportedOperationException("Cannot assign element of immutable List.");\n'
            '  }\n',
            TYPE=self._NarrowInputType(element_type))

    # TODO(sra): Use separate mixins for mutable implementations of List<T>.
    # TODO(sra): Use separate mixins for typed array implementations of List<T>.
    if self._interface.id != 'NodeList':
      template_file = 'immutable_list_mixin.darttemplate'
      template = self._system._templates.Load(template_file)
      self._members_emitter.Emit(template, E=DartType(element_type))

  def AddAttribute(self, getter, setter):
  
    html_getter_name = self._shared.RenameInHtmlLibrary(
      self._interface, getter.id, 'get:')
    html_setter_name = self._shared.RenameInHtmlLibrary(
      self._interface, getter.id, 'set:')

    if not html_getter_name:
      getter = None
    if not html_setter_name:
      setter = None

    if not getter and not setter:
      return

    if ((getter and (html_getter_name != getter.id or
                     self._shared.MaybeReturnDocument(getter.type.id))) or
        (setter and (html_setter_name != setter.id or
                     self._shared.MaybeReturnDocument(setter.type.id))) or
        self._interface.id == 'Document'):
      if getter:
        self._AddRenamingGetter(getter, html_getter_name)
      if setter:
        self._AddRenamingSetter(setter, html_setter_name)
      return

    # If the (getter, setter) pair is shadowing, we can't generate a shadowing
    # field (Issue 1633).
    (super_getter, super_getter_interface) = self._FindShadowedAttribute(getter)
    (super_setter, super_setter_interface) = self._FindShadowedAttribute(setter)
    if super_getter or super_setter:
      if getter and not setter and super_getter and not super_setter:
        if DartType(getter.type.id) == DartType(super_getter.type.id):
          # Compatible getter, use the superclass property.  This works because
          # JavaScript will do its own dynamic dispatch.
          output_type = getter and self._NarrowOutputType(getter.type.id)
          self._members_emitter.Emit(
              '\n'
              '  // Use implementation from $SUPER.\n'
              '  // final $TYPE $NAME;\n',
              SUPER=super_getter_interface.id,
              NAME=getter.id,
              TYPE=output_type)
          return

      self._members_emitter.Emit('\n  // Shadowing definition.')
      self._AddAttributeUsingProperties(getter, setter)
      return

    output_type = getter and self._NarrowOutputType(getter.type.id)
    input_type = setter and self._NarrowInputType(setter.type.id)
    if getter and setter and input_type == output_type:
      self._members_emitter.Emit(
          '\n  $TYPE $NAME;\n',
          NAME=getter.id,
          TYPE=output_type)
      return
    if getter and not setter:
      self._members_emitter.Emit(
          '\n  final $TYPE $NAME;\n',
          NAME=getter.id,
          TYPE=output_type)
      return
    self._AddAttributeUsingProperties(getter, setter)

  def _AddAttributeUsingProperties(self, getter, setter):
    if getter:
      self._AddGetter(getter)
    if setter:
      self._AddSetter(setter)

  def _AddGetter(self, attr):
    self._AddRenamingGetter(attr, attr.id)

  def _AddSetter(self, attr):
    self._AddRenamingSetter(attr, attr.id)

  def _AddRenamingGetter(self, attr, html_name):
    return_type = self._NarrowOutputType(attr.type.id)
    if self._shared.MaybeReturnDocument(attr.type.id):
      self._members_emitter.Emit(
        '\n  $TYPE get $(HTML_NAME)() => '
        '_FixHtmlDocumentReference(_$(HTML_NAME));\n',
        HTML_NAME=html_name,
        NAME=attr.id,
        TYPE=return_type)
      html_name = '_' + html_name
      # For correctness this needs to be the return type of the native helper
      # method due to the fact that the real HTMLDocument object is not typed
      # as a document.  TODO(jacobr): we could simplify this.
      return_type = '_EventTargetImpl'

    self._members_emitter.Emit(
        '\n  $TYPE get $(HTML_NAME)() native "return $(THIS).$NAME;";\n',
        HTML_NAME=html_name,
        NAME=attr.id,
        TYPE=return_type,
        THIS='this.parentNode' if self._interface.id == 'Document' else 'this')

  def _AddRenamingSetter(self, attr, html_name):
    self._members_emitter.Emit(
        '\n  void set $HTML_NAME($TYPE value)'
        ' native "$(THIS).$NAME = value;";\n',
        HTML_NAME=html_name,
        NAME=attr.id,
        TYPE=self._NarrowInputType(attr.type.id),
        THIS='this.parentNode' if self._interface.id == 'Document' else 'this')

  def AddOperation(self, info):
    """
    Arguments:
      info: An OperationInfo object.
    """
    html_name = self._shared.RenameInHtmlLibrary(self._interface, info.name)
    if not html_name:
      return

    maybe_return_document = self._shared.MaybeReturnDocument(info.type_name)

    # Do we need a native body?
    if (self._interface.id == 'Document' or  # Need alternate 'this'
        html_name != info.name or            # renamed operation
        maybe_return_document):              # need to wrap value
      # For example: use window.document instead of his.parentNode.
      return_type = self._NarrowOutputType(info.type_name)
      
      operation_emitter = self._members_emitter.Emit('$!SCOPE',
          THIS=('this.parentNode' if self._interface.id == 'Document'
              else 'this'),
          TYPE=return_type,
          HTML_NAME=html_name,
          NAME=info.name,
          RETURN='' if return_type == 'void' else 'return ',
          PARAMNAMES=info.ParametersAsArgumentList(),
          PARAMS=info.ParametersImplementationDeclaration(
              lambda type_name: self._NarrowInputType(type_name)))

      if maybe_return_document:
        assert len(info.overloads) == 1
        operation_emitter.Emit(
            '\n'
            '  $TYPE $(HTML_NAME)($PARAMS) => '
            '_FixHtmlDocumentReference(_$(HTML_NAME)($PARAMNAMES));\n'
            '\n'
            '  _EventTargetImpl _$(HTML_NAME)($PARAMS)'
            ' native "return $(THIS).$NAME($PARAMNAMES);";\n')
      else:
        operation_emitter.Emit(
            '\n'
            '  $TYPE $(HTML_NAME)($PARAMS)'
            ' native "$(RETURN)$(THIS).$NAME($PARAMNAMES);";\n')
    else:
      self._members_emitter.Emit(
          '\n'
          '  $TYPE $NAME($PARAMS) native;\n',
          TYPE=self._NarrowOutputType(info.type_name),
          NAME=info.name,
          PARAMS=info.ParametersImplementationDeclaration(
              lambda type_name: self._NarrowInputType(type_name)))

  def AddEventAttributes(self, event_attrs):
    event_attrs = _DomToHtmlEvents(self._interface.id, event_attrs)
    events_class = '_' + self._interface.id + 'EventsImpl'
    events_interface = self._interface.id + 'Events'
    self._members_emitter.Emit(
        '\n  $TYPE get on() =>\n    new $TYPE($EVENTTARGET);\n',
        TYPE=events_class,
        EVENTTARGET='_jsDocument' if self._interface.id == 'Document'
            else 'this')

    self._shared._event_classes.add(self._interface.id)

    parent_event_classes = self._shared.GetParentsEventsClasses(
        self._interface)
    if len(parent_event_classes) != 1:
      raise Exception('Only one parent event class allowed '
          + self._interface.id)

    # TODO(jacobr): specify the type of _ptr as EventTarget
    events_members = self._dart_code.Emit(
        '\n'
        'class $CLASSNAME extends $SUPER implements $INTERFACE {\n'
        '  $CLASSNAME(_ptr) : super(_ptr);\n'
        '$!MEMBERS}\n',
        CLASSNAME=events_class,
        INTERFACE=events_interface,
        SUPER='_' + parent_event_classes[0] + 'Impl')

    for event_name in event_attrs:
      if event_name in _html_event_names:
        events_members.Emit(
            "\n"
            "  EventListenerList get $NAME() => _get('$RAWNAME');\n",
            RAWNAME=event_name,
            NAME=_html_event_names[event_name])
      else:
        raise Exception('No known html even name for event: ' + event_name)

# ------------------------------------------------------------------------------

class HtmlFrogSystem(HtmlSystem):

  def __init__(self, templates, database, emitters, output_dir, generator):
    super(HtmlFrogSystem, self).__init__(
        templates, database, emitters, output_dir, generator)
    self._dart_frog_file_paths = []


  def InterfaceGenerator(self,
                         interface,
                         common_prefix,
                         super_interface_name,
                         source_filter):
    """."""
    dart_frog_file_path = self._FilePathForFrogImpl(interface.id)
    self._dart_frog_file_paths.append(dart_frog_file_path)

    template_file = 'impl_%s.darttemplate' % interface.id
    template = self._templates.TryLoad(template_file)
    if not template:
      template = self._templates.Load('frog_impl.darttemplate')

    dart_code = self._emitters.FileEmitter(dart_frog_file_path)
    return HtmlFrogClassGenerator(self, interface, template,
                                  super_interface_name, dart_code, self._shared)

  def GenerateLibraries(self, lib_dir):
    self._GenerateLibFile(
        'html_frog.darttemplate',
        os.path.join(lib_dir, 'html_frog.dart'),
        (self._interface_system._dart_interface_file_paths +
         self._interface_system._dart_callback_file_paths +
         self._dart_frog_file_paths))

  def Finish(self):
    pass

  def _FilePathForFrogImpl(self, interface_name):
    """Returns the file path of the Frog implementation."""
    # TODO(jmesserly): is this the right path
    return os.path.join(self._output_dir, 'html', 'frog',
                        '%s.dart' % interface_name)

# -----------------------------------------------------------------------------

class HtmlDartiumSystem(HtmlSystem):

  def __init__(self, templates, database, emitters, output_dir, generator):
    """Prepared for generating wrapping implementation.

    - Creates emitter for Dart code.
    """
    super(HtmlDartiumSystem, self).__init__(
        templates, database, emitters, output_dir, generator)
    self._shared = HtmlSystemShared(database, generator)
    self._dart_dartium_file_paths = []
    self._wrap_cases = []

  def InterfaceGenerator(self,
                         interface,
                         common_prefix,
                         super_interface_name,
                         source_filter):
    """."""
    dart_dartium_file_path = self._FilePathForImpl(interface.id)
    self._dart_dartium_file_paths.append(dart_dartium_file_path)

    template_file = 'impl_%s.darttemplate' % interface.id
    template = self._templates.TryLoad(template_file)
    # TODO(jacobr): change this name as it is confusing.
    if not template:
      template = self._templates.Load('frog_impl.darttemplate')

    dart_code = self._emitters.FileEmitter(dart_dartium_file_path)
    return HtmlDartiumInterfaceGenerator(self, interface, template,
        super_interface_name, dart_code, self._BaseDefines(interface),
        self._shared)

  def _FilePathForImpl(self, interface_name):
    """Returns the file path of the Frog implementation."""
    # TODO(jmesserly): is this the right path
    return os.path.join(self._output_dir, 'html', 'dartium',
                        '%s.dart' % interface_name)

  def ProcessCallback(self, interface, info):
    pass

  def GenerateLibraries(self, lib_dir):
    # Library generated for implementation.
    self._GenerateLibFile(
        'html_dartium.darttemplate',
        os.path.join(lib_dir, 'html_dartium.dart'),
        (self._interface_system._dart_interface_file_paths +
         self._interface_system._dart_callback_file_paths +
         # FIXME: Move the implementation to a separate library.
         self._dart_dartium_file_paths
         ),
        WRAPCASES='\n'.join(self._wrap_cases))

  def Finish(self):
    pass

# ------------------------------------------------------------------------------

# TODO(jacobr): there is far too much duplicated code between these bindings
# and the Frog bindings.  A larger scale refactoring needs to be performed to
# reduce the duplicated logic.
class HtmlDartiumInterfaceGenerator(object):
  """Generates a wrapper based implementation fo the HTML library that works
  on Dartium.  This is not intended to be the final solution for implementing
  dart:html on Dartium.  Eventually we should generate direct wrapperless
  dart:html bindings that work on dartium."""

  def __init__(self, system, interface, template, super_interface, dart_code,
      base_members, shared):
    """Generates Dart wrapper code for the given interface.

    Args:
      system: system that is executing this generator.
      template: template that output is generated into.
      interface: an IDLInterface instance. It is assumed that all types have
          been converted to Dart types (e.g. int, String), unless they are in
          the same package as the interface.
      super_interface: A string or None, the name of the common interface that
         this interface implements, if any.
      dart_code: an Emitter for the file containing the Dart implementation
          class.
      base_members: a set of names of members defined in a base class.  This is
          used to avoid static member 'overriding' in the generated Dart code.
      shared: functionaly shared across all Html generators. 
    """
    self._system = system
    self._interface = interface
    self._super_interface = super_interface
    self._dart_code = dart_code
    self._base_members = base_members
    self._current_secondary_parent = None
    self._shared = shared
    self._template = template

  def DomObjectName(self):
    return '_documentPtr' if self._interface.id == 'Document' else '_ptr'

  # TODO(jacobr): these 3 methods are duplicated.
  def _NarrowToImplementationType(self, type_name):
    # TODO(sra): Move into the 'system' and cache the result.
    if type_name == 'EventListener':
      # Callbacks are typedef functions so don't have a class.
      return type_name
    if self._system._database.HasInterface(type_name):
      interface = self._system._database.GetInterface(type_name)
      if RecognizeCallback(interface):
        # Callbacks are typedef functions so don't have a class.
        return type_name
      else:
        return self._ImplClassName(type_name)
    return type_name

  def _NarrowInputType(self, type_name):
    return self._NarrowToImplementationType(type_name)

  def _NarrowOutputType(self, type_name):
    return self._NarrowToImplementationType(type_name)

  def StartInterface(self):

    interface = self._interface
    interface_name = interface.id
    self._class_name = self._ImplClassName(interface_name)

    base = None
    if interface.parents:
      supertype = interface.parents[0].type.id
      if not IsDartListType(supertype):
        base = self._ImplClassName(supertype)
      if IsDartCollectionType(supertype):
        # List methods are injected in AddIndexer.
        pass
      else:
        base = self._ImplClassName(supertype)
   
    # TODO(jacobr): this is fragile. There isn't a guarantee that dart:dom
    # will continue to exactly match the IDL names.
    dom_name = interface.javascript_binding_name
    # We hard code the cases for these classes
    if dom_name != 'HTMLHtmlElement' and dom_name != 'Document':
      self._system._wrap_cases.append(
          '    case "%s": return new %s._wrap(domObject);' %
          (dom_name, self._class_name))

    extends = ' extends ' + base if base else ' extends _DOMTypeBase'

    # TODO: Include all implemented interfaces, including other Lists.
    implements = [interface_name]
    element_type = MaybeTypedArrayElementType(self._interface)
    if element_type:
      implements.append('List<' + DartType(element_type) + '>')
    implements_str = ', '.join(implements)

    (self._members_emitter,
     self._top_level_emitter) = self._dart_code.Emit(
        self._template + '$!TOP_LEVEL',
        #class $CLASSNAME$EXTENDS$IMPLEMENTS$NATIVESPEC {
        #$!MEMBERS
        #}
        NATIVESPEC='', # hack to make reusing the same templates work.
        CLASSNAME=self._class_name,
        EXTENDS=extends,
        IMPLEMENTS=' implements ' + implements_str)

    # Document requires a custom wrapper.
    if dom_name != 'Document':
      self._members_emitter.Emit(
          '  $(CLASSNAME)._wrap(ptr) : super._wrap(ptr);\n',
          CLASSNAME=self._class_name)

  def _BaseClassName(self, interface):
    if not interface.parents:
      return '_DOMTypeBase'

    supertype = DartType(interface.parents[0].type.id)

    if IsDartListType(supertype) or IsDartCollectionType(supertype):
      return 'DOMWrapperBase'

    if supertype == 'EventTarget':
      # Most implementors of EventTarget specify the EventListener operations
      # again.  If the operations are not specified, try to inherit from the
      # EventTarget implementation.
      #
      # Applies to MessagePort.
      if not [op for op in interface.operations if op.id == 'addEventListener']:
        return self._ImplClassName(supertype)
      return 'DOMWrapperBase'

    return self._ImplClassName(supertype)

  def _ImplClassName(self, type_name):
    return self._shared._ImplClassName(type_name)

  def FinishInterface(self):
    """."""
    pass

  def AddConstant(self, constant):
    # Constants are already defined on the interface.
    pass

  def _MethodName(self, prefix, name):
    method_name = prefix + name
    if name in self._base_members:  # Avoid illegal Dart 'static override'.
      method_name = method_name + '_' + self._interface.id
    return method_name

  def AddAttribute(self, getter, setter):
    html_getter_name = self._shared.RenameInHtmlLibrary(
      self._interface, getter.id, 'get:')
    html_setter_name = self._shared.RenameInHtmlLibrary(
      self._interface, getter.id, 'set:')

    if getter and html_getter_name:
      self._AddGetter(getter, html_getter_name)
    if setter and html_setter_name:
      self._AddSetter(setter, html_setter_name)

  def _AddGetter(self, attr, html_name):
    if self._shared.MaybeReturnDocument(attr.type.id): 
      self._members_emitter.Emit(
          '\n'
          '  $TYPE get $(HTML_NAME)() => '
          '_FixHtmlDocumentReference(_wrap($(THIS).$NAME));\n',
          NAME=attr.id,
          HTML_NAME=html_name,
          TYPE=DartType(attr.type.id),
          THIS=self.DomObjectName())
    else:
      self._members_emitter.Emit(
        '\n'
        '  $TYPE get $(HTML_NAME)() => _wrap($(THIS).$NAME);\n',
        NAME=attr.id,
        HTML_NAME=html_name,
        TYPE=DartType(attr.type.id),
        THIS=self.DomObjectName())

  def _AddSetter(self, attr, html_name):
    self._members_emitter.Emit(
        '\n'
        '  void set $(HTML_NAME)($TYPE value) { $(THIS).$NAME = _unwrap(value); }\n',
        NAME=attr.id,
        HTML_NAME=html_name,
        TYPE=DartType(attr.type.id),
        THIS=self.DomObjectName())

  def AddSecondaryAttribute(self, interface, getter, setter):
    self._SecondaryContext(interface)
    self.AddAttribute(getter, setter)

  def AddSecondaryOperation(self, interface, info):
    self._SecondaryContext(interface)
    self.AddOperation(info)

  def AddEventAttributes(self, event_attrs):
    event_attrs = _DomToHtmlEvents(self._interface.id, event_attrs)
    events_class = '_' + self._interface.id + 'EventsImpl'
    events_interface = self._interface.id + 'Events'
    self._members_emitter.Emit(
        '\n'
        '  $TYPE get on() {\n'
        '    if (_on == null) _on = new $TYPE($EVENTTARGET);\n'
        '    return _on;\n'
        '  }\n',
        TYPE=events_class,
        EVENTTARGET='_wrappedDocumentPtr' if self._interface.id == 'Document'
            else 'this')

    self._shared._event_classes.add(self._interface.id)

    parent_event_classes = self._shared.GetParentsEventsClasses(
        self._interface)
    if len(parent_event_classes) != 1:
      raise Exception('Only one parent event class allowed '
          + self._interface.id)

    # TODO(jacobr): specify the type of _ptr as EventTarget
    events_members = self._dart_code.Emit(
        '\n'
        'class $CLASSNAME extends $SUPER implements $INTERFACE {\n'
        '  $CLASSNAME(_ptr) : super(_ptr);\n'
        '$!MEMBERS}\n',
        CLASSNAME=events_class,
        INTERFACE=events_interface,
        SUPER='_' + parent_event_classes[0] + 'Impl')

    for event_name in event_attrs:
      if event_name in _html_event_names:
        events_members.Emit(
            "\n"
            "  EventListenerList get $NAME() => _get('$RAWNAME');\n",
            RAWNAME=event_name,
            NAME=_html_event_names[event_name])
      else:
        raise Exception('No known html even name for event: ' + event_name)

  def _SecondaryContext(self, interface):
    if interface is not self._current_secondary_parent:
      self._current_secondary_parent = interface
      self._members_emitter.Emit('\n  // From $WHERE\n', WHERE=interface.id)

  # TODO(jacobr): change this to more directly match the frog version.
  def AddIndexer(self, element_type):
    """Adds all the methods required to complete implementation of List."""
    # We would like to simply inherit the implementation of everything except
    # get length(), [], and maybe []=.  It is possible to extend from a base
    # array implementation class only when there is no other implementation
    # inheritance.  There might be no implementation inheritance other than
    # DOMBaseWrapper for many classes, but there might be some where the
    # array-ness is introduced by a non-root interface:
    #
    #   interface Y extends X, List<T> ...
    #
    # In the non-root case we have to choose between:
    #
    #   class YImpl extends XImpl { add List<T> methods; }
    #
    # and
    #
    #   class YImpl extends ListBase<T> { copies of transitive XImpl methods; }
    #
    if self._HasNativeIndexGetter(self._interface):
      self._EmitNativeIndexGetter(self._interface, element_type)
    else:
      self._members_emitter.Emit(
          '\n'
          '  $TYPE operator[](int index) => _wrap($(THIS)[index]);\n'
          '\n',
          THIS=self.DomObjectName(),
          TYPE=DartType(element_type))

    if self._HasNativeIndexSetter(self._interface):
      self._EmitNativeIndexSetter(self._interface, element_type)
    else:
      # The HTML library implementation of NodeList has a custom indexed setter
      # implementation that uses the parent node the NodeList is associated
      # with if one is available.
      if self._interface.id != 'NodeList':
        self._members_emitter.Emit(
            '\n'
            '  void operator[]=(int index, $TYPE value) {\n'
            '    throw new UnsupportedOperationException("Cannot assign element of immutable List.");\n'
            '  }\n',
            TYPE=DartType(element_type))

    # The list interface for this class is manually generated.
    if self._interface.id == 'NodeList':
      return

    self._members_emitter.Emit(
        '\n'
        '  void add($TYPE value) {\n'
        '    throw new UnsupportedOperationException("Cannot add to immutable List.");\n'
        '  }\n'
        '\n'
        '  void addLast($TYPE value) {\n'
        '    throw new UnsupportedOperationException("Cannot add to immutable List.");\n'
        '  }\n'
        '\n'
        '  void addAll(Collection<$TYPE> collection) {\n'
        '    throw new UnsupportedOperationException("Cannot add to immutable List.");\n'
        '  }\n'
        '\n'
        '  void sort(int compare($TYPE a, $TYPE b)) {\n'
        '    throw new UnsupportedOperationException("Cannot sort immutable List.");\n'
        '  }\n'
        '\n'
        '  void copyFrom(List<Object> src, int srcStart, '
        'int dstStart, int count) {\n'
        '    throw new UnsupportedOperationException("This object is immutable.");\n'
        '  }\n'
        '\n'
        '  int indexOf($TYPE element, [int start = 0]) {\n'
        '    return _Lists.indexOf(this, element, start, this.length);\n'
        '  }\n'
        '\n'
        '  int lastIndexOf($TYPE element, [int start = null]) {\n'
        '    if (start === null) start = length - 1;\n'
        '    return _Lists.lastIndexOf(this, element, start);\n'
        '  }\n'
        '\n'
        '  int clear() {\n'
        '    throw new UnsupportedOperationException("Cannot clear immutable List.");\n'
        '  }\n'
        '\n'
        '  $TYPE removeLast() {\n'
        '    throw new UnsupportedOperationException("Cannot removeLast on immutable List.");\n'
        '  }\n'
        '\n'
        '  $TYPE last() {\n'
        '    return this[length - 1];\n'
        '  }\n'
        '\n'
        '  void forEach(void f($TYPE element)) {\n'
        '    _Collections.forEach(this, f);\n'
        '  }\n'
        '\n'
        '  Collection map(f($TYPE element)) {\n'
        '    return _Collections.map(this, [], f);\n'
        '  }\n'
        '\n'
        '  Collection<$TYPE> filter(bool f($TYPE element)) {\n'
        '    return _Collections.filter(this, new List<$TYPE>(), f);\n'
        '  }\n'
        '\n'
        '  bool every(bool f($TYPE element)) {\n'
        '    return _Collections.every(this, f);\n'
        '  }\n'
        '\n'
        '  bool some(bool f($TYPE element)) {\n'
        '    return _Collections.some(this, f);\n'
        '  }\n'
        '\n'
        '  void setRange(int start, int length, List<$TYPE> from, [int startFrom]) {\n'
        '    throw new UnsupportedOperationException("Cannot setRange on immutable List.");\n'
        '  }\n'
        '\n'
        '  void removeRange(int start, int length) {\n'
        '    throw new UnsupportedOperationException("Cannot removeRange on immutable List.");\n'
        '  }\n'
        '\n'
        '  void insertRange(int start, int length, [$TYPE initialValue]) {\n'
        '    throw new UnsupportedOperationException("Cannot insertRange on immutable List.");\n'
        '  }\n'
        '\n'
        '  List<$TYPE> getRange(int start, int length) {\n'
        '    throw new NotImplementedException();\n'
        '  }\n'
        '\n'
        '  bool isEmpty() {\n'
        '    return length == 0;\n'
        '  }\n'
        '\n'
        '  Iterator<$TYPE> iterator() {\n'
        '    return new _FixedSizeListIterator<$TYPE>(this);\n'
        '  }\n',
        TYPE=DartType(element_type))

  def _HasNativeIndexGetter(self, interface):
    return ('HasIndexGetter' in interface.ext_attrs or
            'HasNumericIndexGetter' in interface.ext_attrs)

  def _EmitNativeIndexGetter(self, interface, element_type):
    method_name = '_index'
    self._members_emitter.Emit(
        '\n  $TYPE operator[](int index) => _wrap($(THIS)[index]);\n',
        TYPE=DartType(element_type),
        THIS=self.DomObjectName(),
        METHOD=method_name)

  def _HasNativeIndexSetter(self, interface):
    return 'HasCustomIndexSetter' in interface.ext_attrs

  def _EmitNativeIndexSetter(self, interface, element_type):
    method_name = '_set_index'
    self._members_emitter.Emit(
        '\n'
        '  void operator[]=(int index, $TYPE value) {\n'
        '    return $(THIS)[index] = _unwrap(value);\n'
        '  }\n',
        THIS=self.DomObjectName(),
        TYPE=DartType(element_type),
        METHOD=method_name)

  def AddOperation(self, info):
    """
    Arguments:
      info: An OperationInfo object.
    """
    html_name = self._shared.RenameInHtmlLibrary(self._interface, info.name)

    if not html_name:
      return

    body = self._members_emitter.Emit(
        '\n'
        '  $TYPE $HTML_NAME($PARAMS) {\n'
        '$!BODY'
        '  }\n',
        TYPE=info.type_name,
        HTML_NAME=html_name,
        PARAMS=info.ParametersImplementationDeclaration())

    # Process in order of ascending number of arguments to ensure missing
    # optional arguments are processed early.
    overloads = sorted(info.overloads,
                       key=lambda overload: len(overload.arguments))
    self._native_version = 0
    fallthrough = self.GenerateDispatch(body, info, '    ', 0, overloads)
    if fallthrough:
      body.Emit('    throw "Incorrect number or type of arguments";\n');

  def GenerateSingleOperation(self,  emitter, info, indent, operation):
    """Generates a call to a single operation.

    Arguments:
      emitter: an Emitter for the body of a block of code.
      info: the compound information about the operation and its overloads.
      indent: an indentation string for generated code.
      operation: the IDLOperation to call.
    """
    # TODO(sra): Do we need to distinguish calling with missing optional
    # arguments from passing 'null' which is represented as 'undefined'?
    def UnwrapArgExpression(name, type):
      # TODO: Type specific unwrapping.
      return '_unwrap(%s)' % (name)

    def ArgNameAndUnwrapper(arg_info, overload_arg):
      (name, type, value) = arg_info
      return (name, UnwrapArgExpression(name, type))

    names_and_unwrappers = [ArgNameAndUnwrapper(info.arg_infos[i], arg)
                            for (i, arg) in enumerate(operation.arguments)]
    unwrap_args = [unwrap_arg for (_, unwrap_arg) in names_and_unwrappers]
    arg_names = ['_unwrap(%s)' % name for (name, _) in names_and_unwrappers]

    argument_expressions = ', '.join(arg_names)
    if info.type_name != 'void':
      # We could place the logic for handling Document directly in _wrap
      # but we chose to place it here so that bugs in the wrapper and
      # wrapperless implementations are more consistent. 
      if self._shared.MaybeReturnDocument(info.type_name): 
        emitter.Emit('$(INDENT)return _FixHtmlDocumentReference('
                     '_wrap($(THIS).$NAME($ARGS)));\n',
                     INDENT=indent,
                     THIS=self.DomObjectName(),
                     NAME=info.name,
                     ARGS=argument_expressions)
      else:
        emitter.Emit('$(INDENT)return _wrap($(THIS).$NAME($ARGS));\n',
                     INDENT=indent,
                     THIS=self.DomObjectName(),
                     NAME=info.name,
                     ARGS=argument_expressions)
    else:
      emitter.Emit('$(INDENT)$(THIS).$NAME($ARGS);\n'
                   '$(INDENT)return;\n',
                   INDENT=indent,
                   THIS=self.DomObjectName(),
                   NAME=info.name,
                   ARGS=argument_expressions)

  def GenerateDispatch(self, emitter, info, indent, position, overloads):
    """Generates a dispatch to one of the overloads.

    Arguments:
      emitter: an Emitter for the body of a block of code.
      info: the compound information about the operation and its overloads.
      indent: an indentation string for generated code.
      position: the index of the parameter to dispatch on.
      overloads: a list of the remaining IDLOperations to dispatch.

    Returns True if the dispatch can fall through on failure, False if the code
    always dispatches.
    """

    def NullCheck(name):
      return '%s === null' % name

    def TypeCheck(name, type):
      return '%s is %s' % (name, type)

    if position == len(info.arg_infos):
      if len(overloads) > 1:
        raise Exception('Duplicate operations ' + str(overloads))
      operation = overloads[0]
      self.GenerateSingleOperation(emitter, info, indent, operation)
      return False

    # FIXME: Consider a simpler dispatch that iterates over the
    # overloads and generates an overload specific check.  Revisit
    # when we move to named optional arguments.

    # Partition the overloads to divide and conquer on the dispatch.
    positive = []
    negative = []
    first_overload = overloads[0]
    (param_name, param_type, param_default) = info.arg_infos[position]

    if position < len(first_overload.arguments):
      # FIXME: This will not work if the second overload has a more
      # precise type than the first.  E.g.,
      # void foo(Node x);
      # void foo(Element x);
      type = DartType(first_overload.arguments[position].type.id)
      test = TypeCheck(param_name, type)
      pred = lambda op: (len(op.arguments) > position and
          DartType(op.arguments[position].type.id) == type)
    else:
      type = None
      test = NullCheck(param_name)
      pred = lambda op: position >= len(op.arguments)

    for overload in overloads:
      if pred(overload):
        positive.append(overload)
      else:
        negative.append(overload)

    if positive and negative:
      (true_code, false_code) = emitter.Emit(
          '$(INDENT)if ($COND) {\n'
          '$!TRUE'
          '$(INDENT)} else {\n'
          '$!FALSE'
          '$(INDENT)}\n',
          COND=test, INDENT=indent)
      fallthrough1 = self.GenerateDispatch(
          true_code, info, indent + '  ', position + 1, positive)
      fallthrough2 = self.GenerateDispatch(
          false_code, info, indent + '  ', position, negative)
      return fallthrough1 or fallthrough2

    if negative:
      raise Exception('Internal error, must be all positive')

    # All overloads require the same test.  Do we bother?

    # If the test is the same as the method's formal parameter then checked mode
    # will have done the test already. (It could be null too but we ignore that
    # case since all the overload behave the same and we don't know which types
    # in the IDL are not nullable.)
    if type == param_type:
      return self.GenerateDispatch(
          emitter, info, indent, position + 1, positive)

    # Otherwise the overloads have the same type but the type is a substype of
    # the method's synthesized formal parameter. e.g we have overloads f(X) and
    # f(Y), implemented by the synthesized method f(Z) where X<Z and Y<Z. The
    # dispatch has removed f(X), leaving only f(Y), but there is no guarantee
    # that Y = Z-X, so we need to check for Y.
    true_code = emitter.Emit(
        '$(INDENT)if ($COND) {\n'
        '$!TRUE'
        '$(INDENT)}\n',
        COND=test, INDENT=indent)
    self.GenerateDispatch(
        true_code, info, indent + '  ', position + 1, positive)
    return True