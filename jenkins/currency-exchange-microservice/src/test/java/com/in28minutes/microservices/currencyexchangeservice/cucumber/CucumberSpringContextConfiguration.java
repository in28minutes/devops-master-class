package com.in28minutes.microservices.currencyexchangeservice.cucumber;

import org.junit.jupiter.api.BeforeEach;
import org.springframework.boot.test.context.SpringBootContextLoader;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.test.context.ContextConfiguration;

import com.in28minutes.microservices.currencyexchangeservice.CurrencyExchangeServiceApplicationH2;

@SpringBootTest(webEnvironment = WebEnvironment.DEFINED_PORT)
@ContextConfiguration(classes = CurrencyExchangeServiceApplicationH2.class, loader = SpringBootContextLoader.class)
public class CucumberSpringContextConfiguration {

  @BeforeEach
  public void setUp() {
  }
}