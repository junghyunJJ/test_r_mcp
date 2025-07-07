# Base R API Server for MCP Bridge
# A clean, extensible R API server using RestRserve

library(RestRserve)
library(jsonlite)

# Configuration
API_PORT <- Sys.getenv("R_API_PORT", "8081")
API_VERSION <- "1.0.0"
SERVICE_NAME <- "R MCP API"

# Helper function to parse request body
parse_request_body <- function(request) {
  if (is.null(request$body)) {
    return(list())
  }

  # RestRserve provides parsed JSON in request$body when Content-Type is application/json
  if (is.list(request$body)) {
    return(request$body)
  }

  # Fallback for other cases
  return(list())
}

# Helper function to create error response
error_response <- function(response, message, status_code = 500) {
  response$set_status_code(status_code)
  response$set_content_type("application/json")
  response$set_body(toJSON(list(
    success = FALSE,
    error = message,
    timestamp = as.character(Sys.time())
  ), auto_unbox = TRUE))
}

# Helper function to create success response
success_response <- function(response, data) {
  response$set_content_type("application/json")
  response$set_body(toJSON(c(
    list(
      success = TRUE,
      timestamp = as.character(Sys.time())
    ),
    data
  ), auto_unbox = TRUE))
}

# Create application
app <- Application$new()

# Add middleware for logging (commented out due to compatibility issues)
# app$add_middleware(
#   Middleware$new(
#     process_request = function(request, response) {
#       cat(sprintf("[%s] %s %s\n", 
#                   Sys.time(), 
#                   request$method, 
#                   request$path))
#     }
#   )
# )

# Health check endpoint
app$add_get(
  path = "/health",
  FUN = function(request, response) {
    success_response(response, list(
      status = "healthy",
      service = SERVICE_NAME,
      version = API_VERSION,
      r_version = R.version.string
    ))
  }
)

# Execute R code endpoint - the most flexible endpoint
app$add_post(
  path = "/api/execute",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      
      # Get code to execute
      code <- body$code
      if (is.null(code) || nchar(code) == 0) {
        error_response(response, "No code provided", 400)
        return()
      }
      
      # Capture output and result
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

# Call R function endpoint
app$add_post(
  path = "/api/call",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      
      # Get function name and arguments
      func_name <- body$func
      args <- body$args
      
      if (is.null(func_name)) {
        error_response(response, "No function name provided", 400)
        return()
      }
      
      # Get the function
      func <- get(func_name)
      if (!is.function(func)) {
        error_response(response, paste(func_name, "is not a function"), 400)
        return()
      }
      
      # Call the function with arguments
      if (is.null(args)) {
        result <- func()
      } else if (is.list(args)) {
        result <- do.call(func, args)
      } else {
        result <- func(args)
      }
      
      success_response(response, list(
        func = func_name,
        result = result,
        class = class(result)
      ))
      
    }, error = function(e) {
      error_response(response, e$message)
    })
  }
)

# Statistics endpoint
app$add_post(
  path = "/api/stats",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      
      # Get data and operation
      data <- as.numeric(body$data)
      operation <- body$operation %||% "summary"
      
      if (is.null(data) || length(data) == 0) {
        error_response(response, "No data provided", 400)
        return()
      }
      
      # Perform operation
      result <- switch(operation,
        "summary" = summary(data),
        "mean" = mean(data, na.rm = TRUE),
        "median" = median(data, na.rm = TRUE),
        "sd" = sd(data, na.rm = TRUE),
        "var" = var(data, na.rm = TRUE),
        "min" = min(data, na.rm = TRUE),
        "max" = max(data, na.rm = TRUE),
        "sum" = sum(data, na.rm = TRUE),
        "quantile" = quantile(data, na.rm = TRUE),
        "fivenum" = fivenum(data),
        {
          error_response(response, paste("Unknown operation:", operation), 400)
          return()
        }
      )
      
      success_response(response, list(
        operation = operation,
        result = result,
        n = length(data),
        na_count = sum(is.na(data))
      ))
      
    }, error = function(e) {
      error_response(response, e$message)
    })
  }
)

# Linear model endpoint
app$add_post(
  path = "/api/lm",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      
      # Support multiple input formats
      if (!is.null(body$formula) && !is.null(body$data)) {
        # Formula-based input
        formula <- as.formula(body$formula)
        data <- as.data.frame(body$data)
        model <- lm(formula, data = data)
      } else if (!is.null(body$x) && !is.null(body$y)) {
        # Simple x,y input
        x <- as.numeric(body$x)
        y <- as.numeric(body$y)
        
        if (length(x) != length(y)) {
          error_response(response, "x and y must have the same length", 400)
          return()
        }
        
        model <- lm(y ~ x)
      } else {
        error_response(response, "Invalid input format. Provide either (formula, data) or (x, y)", 400)
        return()
      }
      
      # Get model summary
      model_summary <- summary(model)
      
      success_response(response, list(
        coefficients = as.list(coef(model)),
        r_squared = model_summary$r.squared,
        adj_r_squared = model_summary$adj.r.squared,
        sigma = model_summary$sigma,
        fstatistic = as.list(model_summary$fstatistic),
        p_values = as.list(model_summary$coefficients[, "Pr(>|t|)"]),
        residuals = list(
          min = min(model$residuals),
          median = median(model$residuals),
          max = max(model$residuals)
        )
      ))
      
    }, error = function(e) {
      error_response(response, e$message)
    })
  }
)

# Data frame operations endpoint
app$add_post(
  path = "/api/dataframe",
  FUN = function(request, response) {
    tryCatch({
      body <- parse_request_body(request)
      
      # Get data and operation
      data <- body$data
      operation <- body$operation %||% "summary"
      
      if (is.null(data)) {
        error_response(response, "No data provided", 400)
        return()
      }
      
      # Convert to data frame
      df <- as.data.frame(data)
      
      # Perform operation
      result <- switch(operation,
        "summary" = summary(df),
        "dim" = dim(df),
        "names" = names(df),
        "head" = head(df, n = body$n %||% 6),
        "tail" = tail(df, n = body$n %||% 6),
        "str" = capture.output(str(df)),
        {
          error_response(response, paste("Unknown operation:", operation), 400)
          return()
        }
      )
      
      success_response(response, list(
        operation = operation,
        result = result,
        nrow = nrow(df),
        ncol = ncol(df)
      ))
      
    }, error = function(e) {
      error_response(response, e$message)
    })
  }
)

# Start server
start_server <- function(port = API_PORT) {
  backend <- BackendRserve$new()
  cat(sprintf("Starting %s on port %s...\n", SERVICE_NAME, port))
  cat(sprintf("R version: %s\n", R.version.string))
  backend$start(app, http_port = as.integer(port))
}

# Run if called directly
if (!interactive()) {
  start_server()
}