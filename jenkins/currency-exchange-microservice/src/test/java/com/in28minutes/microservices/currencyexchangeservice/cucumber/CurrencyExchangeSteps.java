
package com.in28minutes.microservices.currencyexchangeservice.cucumber;

import cucumber.api.java.en.Given;
import cucumber.api.java.en.Then;
import cucumber.api.java.en.When;
import io.restassured.RestAssured;
import io.restassured.builder.RequestSpecBuilder;
import io.restassured.http.ContentType;
import io.restassured.http.Method;
import io.restassured.response.ExtractableResponse;
import io.restassured.response.Response;
import io.restassured.response.ValidatableResponse;

import org.junit.Assert;

import static io.restassured.RestAssured.when;

public class CurrencyExchangeSteps {

    float output = 0f;

    @Given("^conversion rate for (.*) to (.*)$")
    public void conversion_rate_for_fromcurrency_to_tocurrency(String from, String to) throws Exception {
        RestAssured.requestSpecification = new RequestSpecBuilder()
                .setContentType(ContentType.JSON)
                .setAccept(ContentType.JSON)
                .build();
        String url = "http://localhost:8000/currency-exchange/from/"+from+"/to/"+to;
        System.out.println(url);
		Response request = when().request(Method.GET,url);
		ValidatableResponse then = request.then();
		ValidatableResponse statusCode = then.statusCode(200);
		ExtractableResponse<Response> extract = statusCode.extract();
		//then.extract().path("");
		output = extract.path("conversionMultiple");
    }

    @When("^the system is asked to provide the conversion rate$")
    public void the_system_is_asked_to_provide_the_conversion_rate() throws Exception {
    }

    @Then("^It should output (.*)$")
    public void thenCheckOutput(float response) {
       Assert.assertEquals(output, response,0.5);

    }

    public static void main(String[] args) {
    }
}

