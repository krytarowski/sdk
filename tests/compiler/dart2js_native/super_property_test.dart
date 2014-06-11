// Copyright (c) 2013, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

import "package:expect/expect.dart";

// Tests super setter where the HInvokeSuper is using interceptor aka
// explicit-receiver calling convention.

class A native "A" {
  var foo;
  get_foo() => foo;
  set bar(value) => foo = value;
}

class B extends A native "B" {
  set foo(value) {
    super.foo = value;
  }
  get foo => super.foo;
}

class C {
  var foo;
  get_foo() => foo;
  set bar(value) => foo = value;
}

class D extends C {
  set foo(value) {
    super.foo = value;
  }
  get foo => super.foo;
}

makeA() native;
makeB() native;

void setup() native """
// This code is all inside 'setup' and so not accesible from the global scope.
function A(){}
function B(){}
makeA = function(){return new A};
makeB = function(){return new B};
""";

testThing(a) {
  a.foo = 123;
  Expect.equals(123,  a.foo);
  Expect.equals(123,  a.get_foo());

  a.bar = 234;
  Expect.equals(234,  a.foo);
  Expect.equals(234,  a.get_foo());
}

main() {
  setup();
  var things = [makeA(), makeB(), new C(), new D()];
  var test = testThing;
  test(things[0]);
  test(things[1]);
  test(things[2]);
  test(things[3]);
}