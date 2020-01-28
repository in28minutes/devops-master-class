package com.in28minutes.microservices.currencyconversionservice.resource;

import java.math.BigDecimal;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import com.in28minutes.microservices.currencyconversionservice.util.environment.InstanceInformationService;

@RestController
public class CurrencyConversionController {

	private static final Logger LOGGER = LoggerFactory.getLogger(CurrencyConversionController.class);

	@Autowired
	private InstanceInformationService instanceInformationService;

	@Autowired
	private CurrencyExchangeServiceProxy proxy;
	
	@GetMapping("/")
	public String imHealthy() {
		return "{healthy:true}";
	}

	//http://localhost:8100/currency-conversion/from/USD/to/INR/quantity/10
	@GetMapping("/currency-conversion/from/{from}/to/{to}/quantity/{quantity}")
	public CurrencyConversionBean convertCurrency(@PathVariable String from, @PathVariable String to,
			@PathVariable BigDecimal quantity) {

		LOGGER.info("Received Request to convert from {} {} to {}. ", quantity, from, to);

		CurrencyConversionBean response = proxy.retrieveExchangeValue(from, to);

		BigDecimal convertedValue = quantity.multiply(response.getConversionMultiple());

		String conversionEnvironmentInfo = instanceInformationService.retrieveInstanceInfo();

		return new CurrencyConversionBean(response.getId(), from, to, response.getConversionMultiple(), quantity,
				convertedValue, response.getExchangeEnvironmentInfo(), conversionEnvironmentInfo);
	}
}