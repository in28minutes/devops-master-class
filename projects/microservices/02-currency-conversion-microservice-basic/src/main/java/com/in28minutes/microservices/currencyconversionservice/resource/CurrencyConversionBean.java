package com.in28minutes.microservices.currencyconversionservice.resource;

import java.math.BigDecimal;

public class CurrencyConversionBean {

	private Long id;

	private String from;

	private String to;

	private BigDecimal conversionMultiple;

	private BigDecimal quantity;

	private BigDecimal totalCalculatedAmount;

	private String exchangeEnvironmentInfo;
	
	private String conversionEnvironmentInfo;

	public CurrencyConversionBean() {

	}

	public CurrencyConversionBean(Long id, String from, String to, BigDecimal conversionMultiple, BigDecimal quantity,
			BigDecimal totalCalculatedAmount, String exchangeEnvironmentInfo, String conversionEnvironmentInfo) {
		super();
		this.id = id;
		this.from = from;
		this.to = to;
		this.conversionMultiple = conversionMultiple;
		this.quantity = quantity;
		this.totalCalculatedAmount = totalCalculatedAmount;
		this.exchangeEnvironmentInfo = exchangeEnvironmentInfo;
		this.conversionEnvironmentInfo = conversionEnvironmentInfo;
	}

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getFrom() {
		return from;
	}

	public void setFrom(String from) {
		this.from = from;
	}

	public String getTo() {
		return to;
	}

	public void setTo(String to) {
		this.to = to;
	}

	public BigDecimal getConversionMultiple() {
		return conversionMultiple;
	}

	public void setConversionMultiple(BigDecimal conversionMultiple) {
		this.conversionMultiple = conversionMultiple;
	}

	public BigDecimal getQuantity() {
		return quantity;
	}

	public void setQuantity(BigDecimal quantity) {
		this.quantity = quantity;
	}

	public BigDecimal getTotalCalculatedAmount() {
		return totalCalculatedAmount;
	}

	public void setTotalCalculatedAmount(BigDecimal totalCalculatedAmount) {
		this.totalCalculatedAmount = totalCalculatedAmount;
	}

	public String getExchangeEnvironmentInfo() {
		return exchangeEnvironmentInfo;
	}

	public void setExchangeEnvironmentInfo(String environmentInfo) {
		this.exchangeEnvironmentInfo = environmentInfo;
	}

	public String getConversionEnvironmentInfo() {
		return conversionEnvironmentInfo;
	}

	public void setConversionEnvironmentInfo(String conversionEnvironmentInfo) {
		this.conversionEnvironmentInfo = conversionEnvironmentInfo;
	}

}