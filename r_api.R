# Refactored Hello R API Server
# A standalone version with helper functions

library(RestRserve)
library(jsonlite)

# Configuration
API_PORT <- 8081
API_VERSION <- "1.0.0"
SERVICE_NAME <- "Hello R API (Refactored)"

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

###########################################
###########################################
###########################################


# Hello endpoint - simplified
app$add_post(
    path = "/api/hello",
    FUN = function(request, response) {
        tryCatch({
            body <- parse_request_body(request)
            name <- if(is.null(body$name)) "World" else body$name
            
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
            
            a <- as.numeric(if(is.null(body$a)) 0 else body$a)
            b <- as.numeric(if(is.null(body$b)) 0 else body$b)
            
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

# Simple stats endpoint
app$add_post(
    path = "/api/stats",
    FUN = function(request, response) {
        tryCatch({
            body <- parse_request_body(request)
            
            # Get data and operation
            data <- as.numeric(body$data)
            operation <- if(is.null(body$operation)) "mean" else body$operation
            
            if (is.null(data) || length(data) == 0) {
                error_response(response, "No data provided", 400)
                return()
            }
            
            # Perform operation
            result <- switch(operation,
                "mean" = mean(data, na.rm = TRUE),
                "median" = median(data, na.rm = TRUE),
                "sd" = sd(data, na.rm = TRUE),
                "var" = var(data, na.rm = TRUE),
                "min" = min(data, na.rm = TRUE),
                "max" = max(data, na.rm = TRUE),
                "sum" = sum(data, na.rm = TRUE),
                {
                    error_response(response, paste("Unknown operation:", operation), 400)
                    return()
                }
            )
            
            success_response(response, list(
                operation = operation,
                result = result,
                n = length(data)
            ))
            
        }, error = function(e) {
            error_response(response, e$message)
        })
    }
)


# Linear regression endpoint
app$add_post(
    path = "/api/lm",
    FUN = function(request, response) {
        tryCatch({
            body <- parse_request_body(request)
            
            # Get x and y data
            x <- as.numeric(body$x)
            y <- as.numeric(body$y)
            
            # Validate input
            if (is.null(x) || length(x) == 0) {
                error_response(response, "No x data provided", 400)
                return()
            }
            
            if (is.null(y) || length(y) == 0) {
                error_response(response, "No y data provided", 400)
                return()
            }
            
            if (length(x) != length(y)) {
                error_response(response, "x and y must have the same length", 400)
                return()
            }
            
            if (length(x) < 2) {
                error_response(response, "At least 2 data points are required", 400)
                return()
            }
            
            # Fit linear model
            model <- lm(y ~ x)
            summary_model <- summary(model)
            
            # Extract results
            coefficients <- coef(model)
            
            success_response(response, list(
                coefficients = list(
                    intercept = coefficients[1],
                    slope = coefficients[2]
                ),
                r_squared = summary_model$r.squared,
                p_value = summary_model$coefficients[2, 4],
                residual_std_error = summary_model$sigma,
                n = length(x)
            ))
            
        }, error = function(e) {
            error_response(response, e$message)
        })
    }
)


# Create backend and start server
backend <- BackendRserve$new()
cat(sprintf("Starting %s on port %s...\n", SERVICE_NAME, API_PORT))
cat(sprintf("R version: %s\n", R.version.string))
backend$start(app, http_port = API_PORT)