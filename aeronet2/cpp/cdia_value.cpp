// Decision value of one position measurement; same fixed-grid rule as aeronet2.cdia.decision.
#include <cmath>
#include <cstddef>

namespace {
constexpr int kGridN = 4001;
constexpr double kHalfWidth = 9.0;
constexpr double kMinVar = 1e-12;
constexpr double kInvSqrt2 = 0.70710678118654752440;
constexpr double kInvSqrt2Pi = 0.39894228040143267794;

inline double ndtr(double x) { return 0.5 * std::erfc(-x * kInvSqrt2); }

double bayes_error(double d, double s2) {
    return ndtr(-std::fabs(d) / std::sqrt(s2 > kMinVar ? s2 : kMinVar));
}
}  // namespace

extern "C" {

double cdia_decision_value(double d, double s2, double v) {
    if (v > s2 - kMinVar) v = s2 - kMinVar;
    if (v <= 0.0) return 0.0;
    const double sp = std::sqrt(s2 - v), sv = std::sqrt(v);
    const double h = 2.0 * kHalfWidth / (kGridN - 1);
    double acc = 0.0;
    for (int k = 0; k < kGridN; ++k) {
        const double xi = -kHalfWidth + h * k;
        double w = std::exp(-0.5 * xi * xi) * kInvSqrt2Pi * h;
        if (k == 0 || k == kGridN - 1) w *= 0.5;
        acc += w * ndtr(-std::fabs(d + sv * xi) / sp);
    }
    return bayes_error(d, s2) - acc;
}

// Batch form for an allocator that scores every candidate action in one call.
void cdia_decision_value_batch(const double* d, const double* s2, const double* v, double* out, std::size_t n) {
    for (std::size_t i = 0; i < n; ++i) out[i] = cdia_decision_value(d[i], s2[i], v[i]);
}

}  // extern "C"
