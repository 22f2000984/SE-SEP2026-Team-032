<script setup>
import BrandLogo from '../components/common/BrandLogo.vue';
</script>

<template>
  <div class="auth-page">
    <div class="auth-shell">
      <section class="auth-hero">
        <router-link class="auth-brand" to="/login">
          <BrandLogo variant="light" />
          <span class="auth-divider"></span>
          <b>Mentor<br />Connect</b>
        </router-link>
        <div class="auth-message">
          <div class="auth-kicker">★ &nbsp; STUDENT MENTORING PLATFORM</div>
          <h2>Learn.<br />Grow.<br /><em>Together.</em></h2>
          <p>Connect with experienced mentors, gain guidance, and achieve your academic and career goals.</p>
          <div class="auth-benefits">
            <span>◎<small>Get Guidance</small></span>
            <span>♧<small>Build Connections</small></span>
            <span>↗<small>Achieve Your Goals</small></span>
          </div>
        </div>
        <small class="auth-foot">Student Mentoring &amp; Career Support</small>
      </section>
      <section class="auth-panel"><slot /></section>
    </div>
  </div>
</template>
