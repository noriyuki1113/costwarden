"use strict";
/*
 * CostWarden calculator — pure cost math.
 * model: { input_per_token, output_per_token } (USD per single token,
 * exactly as published in LiteLLM's model_prices data).
 */
function computeCost(model, inputTokens, outputTokens, requestsPerDay) {
  var perRequest =
    inputTokens * model.input_per_token + outputTokens * model.output_per_token;
  var daily = perRequest * requestsPerDay;
  return {
    perRequest: perRequest,
    daily: daily,
    monthly: daily * 30
  };
}

var CALC_API = { computeCost: computeCost };
if (typeof module !== "undefined" && module.exports) module.exports = CALC_API;
if (typeof window !== "undefined") window.CWCalc = CALC_API;
