Feature: Cucumber hello world example

  Scenario Outline: Hello World
    Given A String name <name>
    When sayHello method of HelloWorld.java is called
    Then It should return <output>

    Examples:
      |	name	|	output		|
      |	World	|	Hello World	|
      |	Ravi	|	Hello Ravi	|