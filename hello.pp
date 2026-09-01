class hello_world {
  notify { 'hello-world':
    message => 'Hello, world!',
  }
}

include hello_world
