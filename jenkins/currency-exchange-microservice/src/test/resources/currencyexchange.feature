Feature: Currency Exchange Rate

  Scenario Outline: Verify conversion rate exposed correctly
    Given conversion rate for <fromcurrency> to <tocurrency>
    When the system is asked to provide the conversion rate
    Then It should output <output>

    Examples:
      |	fromcurrency	|	tocurrency	|	output		|
      |	EUR	|	INR	    |	75	|
      |	USD	|	INR	    |	65	|