# Refactored Hello R API Server using base functions
# This is a cleaner version that uses the base_r_api.R helpers

# Source the base API functions
source("base_r_api.R")

# Create application
app <- Application$new()

# Hello endpoint - simplified
app$add_post(
  path = "/api/hello",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      name <- body$name %||% "World"
      
      greeting <- paste("Hello", name, "from R!")
      
      success_response(response, list(
        message = greeting,
        r_version = R.version.string
      ))
      
    }, error = function(e) {
      error_response(response, e$message)
    })
  }
)

# Addition endpoint - simplified  
app$add_post(
  path = "/api/add",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      
      a <- as.numeric(body$a %||% 0)
      b <- as.numeric(body$b %||% 0)
      
      result <- a + b
      
      success_response(response, list(
        a = a,
        b = b,
        result = result,
        operation = "addition"
      ))
      
    }, error = function(e) {
      error_response(response, e$message)
    })
  }
)

# You can also use the more powerful endpoints from base_r_api.R
# Just add them to this app instance if needed:

# For example, to add the execute endpoint:
app$add_post(
  path = "/api/execute",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      
      code <- body$code
      if (is.null(code) || nchar(code) == 0) {
        error_response(response, "No code provided", 400)
        return()
      }
      
      output <- capture.output({
        result <- eval(parse(text = code))
      })
      
      success_response(response, list(
        result = result,
        output = output,
        class = class(result)
      ))
      
    }, error = function(e) {
      error_response(response, e$message)
    })
  }
)

# Start server
if (!interactive()) {
  start_server(8081)
}