package com.in28minutes.microservices.currencyexchangeservice.cucumber;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

import org.junit.jupiter.api.Assertions;

import com.in28minutes.microservices.currencyexchangeservice.HelloWorld;

public class HelloWorldSteps {

    private HelloWorld helloWorld = new HelloWorld();


    private String name = "";

    private String output = "";

    @Given("^A String name (.*)$")
    public void givenInput(String name) {
        this.name = name;
    }

    @When("^sayHello method of HelloWorld.java is called$")
    public void whenBusinessLogicCalled() {
        output = helloWorld.sayHello(name);
    }

    @Then("^It should return (.*)$")
    public void thenCheckOutput(String response) {
        Assertions.assertEquals(output, response);
    }

    public static void main(String[] args) {
    }
}
