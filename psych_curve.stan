data{
  int<lower=1> n;
  vector[n] log_delta;
  int correct[n];
  int totals[n];

  real sigma;
  real miss;
  real tmin; real tmax;
}
transformed data{
  real sqrt_2;
  sqrt_2 <- sqrt(2);
}
parameters{
  real<lower=tmin,upper=tmax> theta;
}
model{
  for(i in 1:n){
    real p;
    p <- (miss/2) + (1-miss)*Phi_approx(exp((log_delta[i] - theta)*sigma)/sqrt_2);
    correct[i] ~ binomial(totals[i],p);
  }
}
