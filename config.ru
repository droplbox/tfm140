run lambda { |env| [ 
  200, 
  {"content-type" => "text/html"}, 
  "hello from russia, time is now #{ Time.now }" 
  ] }